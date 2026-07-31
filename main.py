from utilities import get_temperature , available_fluids
from CoolProp.CoolProp import PropsSI
import CoolProp
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

print(CoolProp.__version__)
T0 = 20  #default ambient temperature
T_source = 250
#available_fluids = available_fluids()

def calculate_thermodynamics(fluids , T_source : float ,P0 : float, P_super_heat : float  , mass_flow_rate : float = 1):
    global T0
    fluid,comp = list(fluids.keys()) , list(fluids.values())
    fluid_string = "&".join(fluid)

    state = CoolProp.AbstractState("HEOS",fluid_string)
    state.set_mole_fractions(comp)
    state.build_phase_envelope("")

    # print(fluid_string)

    #state [1] after condenser    
    state.update(CoolProp.QT_INPUTS , 0 , T0 + 273.15 )
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


class OptimizeProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=3,n_obj=1, n_ieq_constr =3,
                          xl = np.array([0 , 0 , 0]),
                          xu = np.array([1 , 1 , 1]))
        """
         take P_source and P0 as given 
         assumed isentropic turbine and pump
         assumed no heat lose in cycle
         assumed no pressure drop in cycle

         maximize cycle efficiency
        """
    def _evaluate(self, x, out, *args, **kwargs):
        global T_source
        # TODO: add fluid sampling here
        # TODO: for each goal make separate file  
        normalized_x = x / np.sum(x)
        print(normalized_x)
        fluids = {"R134a":normalized_x[0],"R32":normalized_x[1],"R125":normalized_x[2]}
        try:
            props = calculate_thermodynamics(fluids,T_source, 10e3 , 2e6)

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
    temperatures_at_Isfahan = get_temperature(51.6804 , 32.6613 , 2025 , (6 ,7 ,8))
    print("temperature of Isfahan city during summer:" , temperatures_at_Isfahan)
    T0 = np.sum(temperatures_at_Isfahan) / 3
    algorithm = NSGA2(pop_size=80)
    p = OptimizeProblem()
    res = minimize(p , algorithm , ("n_gen",100) , seed = 1)
    print(res.X)
    
if __name__ == '__main__':
    main()