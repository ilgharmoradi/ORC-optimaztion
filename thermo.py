import CoolProp
from config import *

def calculate_thermodynamics(fluids , T_evap : float , T0 : float,P_super_heat : float  , mass_flow_rate : float = 1): 
    fluid,comp = list(fluids.keys()) , list(fluids.values())
    fluid_string = "&".join(fluid)
    state = CoolProp.AbstractState("SRK",fluid_string)
    state.set_mole_fractions(comp)
    #state.build_phase_envelope("")

    T_cond = T0 + cooling_temperature_difference #small temperature difference for air cooling
    state.update(CoolProp.QT_INPUTS , 0 , T_cond + 273.15)
    P0 = state.p()
    P_super_heat = int(P_super_heat)
    # print(fluid_string)

    #state [1] after condenser    
    state.update(CoolProp.PQ_INPUTS , P0 , 0 )
    h1 = state.hmass()
    s2 = state.smass()

    # state [2] after pump
    state.update(CoolProp.PSmass_INPUTS , P_super_heat , s2)
    h2 = state.hmass()

    
    state.update(CoolProp.PT_INPUTS , P_super_heat , T_evap + 273.15)
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
    return ( w_net * mass_flow_rate , eta , q_out , P0)
