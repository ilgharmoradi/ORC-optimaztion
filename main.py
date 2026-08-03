#TODO add comments around
from itertools import combinations
from utilities import get_temperature , available_fluids , normalization , ORC_FLUIDS
import CoolProp
from thermo import calculate_thermodynamics
from config import *
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

import csv
import time
print(ORC_FLUIDS)

print("coolprop version:" , CoolProp.__version__)
available_fluids = available_fluids()

n = 0
 
class OptimizeProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=len(ORC_FLUIDS) + 1,n_obj=2, n_ieq_constr =4,
                          xl = np.zeros(len(ORC_FLUIDS) + 1),
                          xu = np.array([*[1]*len(ORC_FLUIDS) , 10e6]))
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
        normalized_x = normalization(x[:len(ORC_FLUIDS)])
        masked_fluids = np.array(ORC_FLUIDS)[normalized_x != 0]

        for i in list(combinations(masked_fluids , 2)):
            if not (set(i) in  available_fluids):
                out["F"] = [1e6 , 1e6]
                out["G"] = [1e6, 1e6, 1e6 , 1000e6]
                print("incompatible fluids")
                return
            

        fluids = dict(zip(masked_fluids , normalized_x[normalized_x != 0]))
        if should_print_run: print(n , masked_fluids)
        n += 1
        try:
            props = calculate_thermodynamics(fluids,T_source,T0 , x[-1])

            g1 = -props[0]
            g2 = -props[1]
            g3 = -props[2]
            g4 = props[3] - x[-1]

            out["F"] = [-props[1] , -props[0]]

            out["G"] = [g1 , g2 , g3 , g4]
        except Exception as e:
            # print(e)
            out["F"] = [1e6 , 1e6]
            out["G"] = [1e6, 1e6, 1e6 , 1000e6]
            return

def main():
    global T0
    temperatures_at_Isfahan,error = get_temperature(51.6804 , 32.6613 , 2025 , (6 ,7 ,8))
    if error != 0:
        T0 = 40
    else:
        print("temperature of Isfahan city during summer:" , temperatures_at_Isfahan)
        T0 = np.sum(temperatures_at_Isfahan) / 3
    algorithm = NSGA2(pop_size=20)
    T0 = 20
    p = OptimizeProblem()
    with open( f"results/{int(time.time())}.csv" if run_name.strip() == "" else f"results/{run_name}.csv" , "w") as f:
        csv_handler = csv.writer(f)
        csv_handler.writerow(["run N" , *ORC_FLUIDS , "eta" , "P"])

        t_start = time.time()
        for i in range(0 , 1):
            res = minimize(p , algorithm , ("n_gen",40) , seed = i)
            normalized_x = normalization (res.X[:,:len(ORC_FLUIDS)])
            for j in range(len(normalized_x)):
                csv_handler.writerow([i , *normalized_x[j] , -res.F[j][0] , res.X[j][len(ORC_FLUIDS)]])

        t_end = time.time()
        print("calculation time : " , t_end - t_start)

if __name__ == '__main__':
    main()