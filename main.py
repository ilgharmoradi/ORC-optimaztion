from itertools import combinations
from utilities import get_temperature , available_fluids , normalization , normalize_k
import CoolProp
from thermo import calculate_thermodynamics
from config import *
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from math import floor

import csv
import time

print("coolprop version:" , CoolProp.__version__)

if thermodynamic_calculation_method == "REFPROP":
        if REFPROP_path.strip() == "" : raise Exception("you must specify REFPROP installation path")
        CoolProp.CoolProp.set_config_string(CoolProp.CoolProp.ALTERNATIVE_REFPROP_PATH,REFPROP_path)
        print("using REFPROP version:",CoolProp.CoolProp.get_global_param_string("REFPROP_version"))
if max_n_fluids != None and n_fluids != None:
    raise Exception("n_fluids and max_n_fluids are incompatible variables and one must be None at all time")
 
# gets the available fluids mixtures based on thermodynamics calculation method
available_fluids = available_fluids()

n = 0
 
class OptimizeProblem(ElementwiseProblem):
    def __init__(self):
        n_var = len(ORC_FLUIDS) + 1
        n_obj= 3
        n_ieq_constr = 5
        xl = np.zeros(len(ORC_FLUIDS) + 1)
        xu = np.array([*[1]*len(ORC_FLUIDS) , max_boiler_pressure])

        self.penalty_G = [1e6, 1e6, 1e6, 1e6 , 1e6 ]
        self.penalty_F = [1e6 , 1e6 , 1e6]
        

        if max_n_fluids != None:
            n_var = len(ORC_FLUIDS) + 2
            xl = np.zeros(len(ORC_FLUIDS) + 2)
            xu = np.array([*[1]*(len(ORC_FLUIDS) + 1), 10e6])
        if max_n_fluids and should_minimize_n_fluids:
            self.penalty_F.append(1e6)
            n_obj+= 1
            
        super().__init__(n_var=n_var,n_obj=n_obj, n_ieq_constr = n_ieq_constr,
                          xl =xl,
                          xu = xu)
        """
         take P_source as design value or parameter to optimize
         assumed isentropic turbine and pump
         assumed no heat lose in cycle
         assumed no pressure drop in cycle

         maximize cycle efficiency
        """

    def _evaluate(self, x, out, *args, **kwargs):
        global T_source , n
        # TODO: for each goal make separate file  
        normalized_x = None
        if max_n_fluids != None:
            k_fluids = normalize_k(x[-2])
            print(k_fluids)
            normalized_x = normalization(x[:len(ORC_FLUIDS)] , k_fluids)
        else:
           normalized_x = normalization(x[:len(ORC_FLUIDS)])
        masked_fluids = np.array(ORC_FLUIDS)[normalized_x != 0]
        # print(normalized_x)
        n += 1

        for i in list(combinations(masked_fluids , 2)):
            if not (set(i) in  available_fluids):
                out["F"] = self.penalty_F
                out["G"] = self.penalty_G
                print("incompatible fluids")
                return
            

        fluids = dict(zip(masked_fluids , normalized_x[normalized_x != 0]))
        if should_print_run: print(n , masked_fluids)
        try:
            print(n)
            props = calculate_thermodynamics(fluids,T_source,T0 , x[-1])
            g1 = -props["w_net"]
            g2 = -props["eta"]
            g3 = -props["q_out"]
            g4 = props["P0"] - x[-1]
            g5 = -(props["Q_turbine_out"] - max_turbine_outlet_quality)
            
            out_F = [-props["eta"] , -props["w_net"], -props["Q_turbine_out"] ]                                                         #n fluid
            if max_n_fluids and should_minimize_n_fluids: out_F.append(k_fluids)
            out["G"] = [g1 , g2 , g3 , g4 , g5]

            out["F"] = np.copy(out_F)

        except Exception as e:
            print(e)
            out["F"] = self.penalty_F
            out["G"] = self.penalty_G
            return

def main():
    global T0
    temperatures_at_Isfahan,error = get_temperature(51.6804 , 32.6613 , 2025 , (6 ,7 ,8))
    if error == 0:
        print("temperature of Isfahan city during summer:" , temperatures_at_Isfahan)
        T0 = np.sum(temperatures_at_Isfahan) / 3
    print("T0:" , T0)
    algorithm = NSGA2(pop_size=n_pop)
    p = OptimizeProblem()

    with open( f"results/{int(time.time())}.csv" if run_name.strip() == "" else f"results/{run_name}.csv" , "w") as f:
        csv_handler = csv.writer(f)
        csv_handler.writerow(["run N" , *ORC_FLUIDS , "eta" , "n fluid","P","Q"])
        #F[0] -> eta F[1] -> net_work F[2] -> Q F[3] -> n_fluid
        t_start = time.time()
        for i in range(1 , n_run+1):
            res = minimize(p , algorithm , ("n_gen",n_gen) , seed = i)
            for j in range(len(res.X)):
                normalized_x = normalization (res.X[j,:len(ORC_FLUIDS)] , int(normalize_k(res.X[j][-2])) if max_n_fluids else None)
                csv_handler.writerow([i , *normalized_x , -res.F[j][0] ,normalize_k(res.X[j][-2]) if max_n_fluids else n_fluids ,res.X[j][-1] ,res.F[j][2]])
        t_end = time.time()

        print("calculation time : " , t_end - t_start)

if __name__ == '__main__':
    main()