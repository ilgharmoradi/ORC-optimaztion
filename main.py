from utilities import get_temperature , available_fluids , normalization
from CoolProp.CoolProp import PropsSI
import CoolProp
import CoolProp.Plots
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

import csv
import time

print("coolprop version:" , CoolProp.__version__)
run_name = "run with T0 = 40"
T0 = 20  #default ambient temperature
T_source = 250
# available_fluids = available_fluids()


def calculate_thermodynamics(fluids , T_source : float , P_super_heat : float  , mass_flow_rate : float = 1):
    global T0
    fluid,comp = list(fluids.keys()) , list(fluids.values())
    fluid_string = "&".join(fluid)

    state = CoolProp.AbstractState("SRK",fluid_string)
    state.set_mole_fractions(comp)
    #state.build_phase_envelope("")

    T_cond = T0 + 15 #small temperature difference for air cooling
    state.update(CoolProp.QT_INPUTS , 0 , T_cond + 273.15)
    P0 = state.p()
    # print(fluid_string)

    #state [1] after condenser    
    state.update(CoolProp.PQ_INPUTS , P0 , 0 )
    h1 = state.hmass()
    s2 = state.smass()

    # state [2] after pump
    state.update(CoolProp.PSmass_INPUTS , P_super_heat , s2)
    h2 = state.hmass()

    state.update(CoolProp.PT_INPUTS , P_super_heat , T_source + 273.15)
    h3 = state.hmass()
    s4 = state.smass()

    state.update(CoolProp.PSmass_INPUTS , P0 , s4)
    h4 = state.hmass()

    w_turbine = h3 - h4
    w_pump = h2 - h1
    w_net = w_turbine - w_pump
    q_in = h3-h2
    q_out = h4 - h1
    eta = w_net / q_in
    return ( w_net * mass_flow_rate , eta , q_out)

n = 0

class OptimizeProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=3,n_obj=1, n_ieq_constr =3,
                          xl = np.array([0 , 0 , 0]),
                          xu = np.array([1 , 1 , 1]))
        """
         take P_source as design value or parameter to optimize
         assumed isentropic turbine and pump
         assumed no heat lose in cycle
         assumed no pressure drop in cycle

         maximize cycle efficiency
        """
    def _evaluate(self, x, out, *args, **kwargs):
        global T_source , n
        # TODO: add fluid sampling here
        # TODO: for each goal make separate file  
        normalized_x = normalization(x)
        # print(n , normalized_x)
        fluids = {"R134a":normalized_x[0],"R32":normalized_x[1],"R125":normalized_x[2]}
        n += 1
        try:
            props = calculate_thermodynamics(fluids,T_source, 6e6)

            g1 = -props[0]
            g2 = -props[1]
            g3 = -props[2]

            out["F"] = [-props[1]]
            out["G"] = [g1 , g2 , g3]
        except Exception as e:
            print(e)
            out["F"] = [1e6]
            out["G"] = [1e6, 1e6, 1e6]
            return

def main():
    global T0
    temperatures_at_Isfahan,error = get_temperature(51.6804 , 32.6613 , 2025 , (6 ,7 ,8))
    if error != 0:
        T0 = 40
    else:
        print("temperature of Isfahan city during summer:" , temperatures_at_Isfahan)
        T0 = np.sum(temperatures_at_Isfahan) / 3
    algorithm = NSGA2(pop_size=100)
    p = OptimizeProblem()
    with open( f"results/{int(time.time())}.csv" if run_name.strip() == "" else f"results/{run_name}.csv" , "w") as f:
        csv_handler = csv.writer(f)
        csv_handler.writerow(["run N" , "R134a" , "R32" , "R125" , "eta"])

        t_start = time.time()
        for i in range(0 , 10):
            res = minimize(p , algorithm , ("n_gen",80) , seed = i)
            normalized_x = normalization (res.X)
            print(normalized_x)
            # if all(res.X): # type: ignore
            #     csv_handler.writerow([i , normalized_x[0] , normalized_x[1] , normalized_x[2] , -res.F[0]]) # type: ignore
            # else:
            #     csv_handler.writerow([i , 0 , 0 , 0 ,0 ]) 
            # print(res.X)
        t_end = time.time()
        print("calculation time : " , t_end - t_start)

if __name__ == '__main__':
    main()