from itertools import combinations
from utilities import get_temperature , available_fluids , normalization , normalize_k
import CoolProp
from thermo import calculate_thermodynamics
from  load_config import config 
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

import csv
import time
import sys

print("coolprop version:" , CoolProp.__version__)

if config.thermodynamic_calculation_method == "REFPROP":
        if config.REFPROP_path.strip() == "" : raise Exception("you must specify REFPROP installation path")
        CoolProp.CoolProp.set_config_string(CoolProp.CoolProp.ALTERNATIVE_REFPROP_PATH,config.REFPROP_path)
        print("using REFPROP version:",CoolProp.CoolProp.get_global_param_string("REFPROP_version"))
# gets the available fluids mixtures based on thermodynamics calculation method
available_fluids = available_fluids()

n = 0
 
class OptimizeProblem(ElementwiseProblem):
    def __init__(self):
        n_var = len(config.ORC_FLUIDS) + 1
        n_obj= 2
        n_ieq_constr = 5
        xl = np.zeros(len(config.ORC_FLUIDS) + 1)
        xu = np.array([*[1]*len(config.ORC_FLUIDS) , config.max_boiler_pressure])

        self.penalty_G = [1e6, 1e6, 1e6, 1e6 , 1e6 ]
        self.penalty_F = [1e6 , 1e6]
        

        if config.max_n_fluids != None:
            n_var = len(config.ORC_FLUIDS) + 2
            xl = np.zeros(len(config.ORC_FLUIDS) + 2)
            xu = np.array([*[1]*(len(config.ORC_FLUIDS) + 1), config.max_boiler_pressure])
        if config.max_n_fluids and config.should_minimize_n_fluids:
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
        global n
        # TODO: for each goal make separate file  
        normalized_x = None
        if config.max_n_fluids != None:
            k_fluids = normalize_k(x[-2])
            normalized_x = normalization(x[:len(config.ORC_FLUIDS)] , k_fluids)
        else:
           normalized_x = normalization(x[:len(config.ORC_FLUIDS)])
        masked_fluids = np.array(config.ORC_FLUIDS)[normalized_x != 0]
        n += 1

        for i in list(combinations(masked_fluids , 2)):
            if not (set(i) in  available_fluids):
                out["F"] = self.penalty_F
                out["G"] = self.penalty_G
                print("incompatible fluids")
                return
            

        fluids = dict(zip(masked_fluids , normalized_x[normalized_x != 0]))
        if config.should_print_run: print(n , masked_fluids)
        try:
            props = calculate_thermodynamics(fluids,config.T_source,config.T0 , x[-1])
            g1 = -props["w_net"]
            g2 = -props["eta"]
            g3 = -props["q_out"]
            g4 = props["P0"] - x[-1]

            g5 = -(props["Q_turbine_out"] - config.min_turbine_outlet_quality)
            out_F = [-props["eta"] , -props["w_net"] ]                                                         #n fluid
            if config.max_n_fluids and config.should_minimize_n_fluids: out_F.append(k_fluids)
            out["G"] = [g1 , g2 , g3 , g4 , g5]

            out["F"] = np.copy(out_F)

        except Exception as e:
            print(e)
            out["F"] = self.penalty_F
            out["G"] = self.penalty_G
            return

def main():
    global T0
    temperatures_at_Isfahan,error = get_temperature(config.city_location , 2025 , (6 ,7 ,8))
    if error == 0:
        print("temperature of Isfahan city during summer:" , temperatures_at_Isfahan)
        T0 = np.mean(temperatures_at_Isfahan)
    
    print("T0:" , config.T0)
    algorithm = NSGA2(pop_size=config.n_pop)
    p = OptimizeProblem()

    # calculations
    results = []
    t_start = time.time()
    for i in range(1 , config.n_run+1):
        results.append(minimize(p , algorithm , ("n_gen",config.n_gen) , seed = int(time.time())))
    t_end = time.time()
    print("calculations finished\n calculation time : " , t_end - t_start)

    if not any(results): return sys.exit("no solutions found\result file unchanged")
    results_file_name = f"results/{int(time.time())}.csv" if config.run_name.strip() == "" else f"results/{config.run_name}.csv"
    print(f"writing the results to {results_file_name}") 
    with open(results_file_name , "w") as f:
        csv_handler = csv.writer(f)
        csv_handler.writerow(["run N" , *config.ORC_FLUIDS , "eta" , "n fluid","boiler pressure","Q"])
        #F[0] -> eta F[1] -> net_work F[2] -> Q F[3] -> n_fluid
        for i,res in enumerate(results):
            for j in range(len(res.X)):
                normalized_x = normalization (res.X[j,:len(config.ORC_FLUIDS)] , int(normalize_k(res.X[j][-2])) if config.max_n_fluids else None)
                #x[-1] -> boiler pressure
                csv_handler.writerow([i+1 , *normalized_x , -res.F[j][0] ,normalize_k(res.X[j][-2]) if config.max_n_fluids else config.n_fluids ,res.X[j][-1] ,res.F[j][2] if res.F[j][2] != -10 else "not a saturated mixture"])


if __name__ == '__main__':
    main()