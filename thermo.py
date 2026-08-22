import CoolProp
from config import *

def calculate_thermodynamics(fluids , T_evap : float , T0 : float,P_super_heat : float  , 
                             mass_flow_rate : float = 1 , turbine_effi= 1 , pump_effi = 1 , condenser_pressure_drop = 0): 
    fluid,comp = list(fluids.keys()) , list(fluids.values())
    fluid_string = "&".join(fluid)
    state = CoolProp.AbstractState(thermodynamic_calculation_method,fluid_string)
    if len(fluid) != 1: state.set_mole_fractions(comp)

    T_cond = T0 + cooling_temperature_difference #small temperature difference for air cooling
    state.update(CoolProp.QT_INPUTS , 0 , T_cond + 273.15)
    P0 = state.p()
    P_super_heat = int(P_super_heat)

    #state [1] after condenser    
    state.update(CoolProp.PQ_INPUTS , P0 , 0 )
    h1 = state.hmass()
    s2 = state.smass()

    # state [2] after pump
    state.update(CoolProp.PSmass_INPUTS , P_super_heat , s2)
    h2s = state.hmass()
    h2 = (h2s - h1) / pump_effi + h1
    # h2s - h1 / h2a - h1 = n_pump
    
    state.update(CoolProp.PT_INPUTS , P_super_heat , T_evap + 273.15)
    h3 = state.hmass()
    s4 = state.smass()
    # h3a - h4  / h3s - h4 = n

    state.update(CoolProp.PSmass_INPUTS , P0 - condenser_pressure_drop , s4)
    h4s = state.hmass()
    Q_turbine_out = 10
    try:
        Q_turbine_out = state.Qmass()
    except ValueError as e:
        if str(e) == "Qmass requires a two-phase state (0 <= Q <= 1)":
            Q_turbine_out = 10

    #turbine efficiency  
    h4 = h3 - turbine_effi * (h3 - h4s)

    w_turbine = h3 - h4
    w_pump = h2 - h1
    w_net = w_turbine - w_pump
    q_in = h3-h2
    q_out = h4 - h1
    eta = w_net / q_in
    return {
            "w_net": w_net * mass_flow_rate ,
            "eta": eta , 
            "q_out":q_out ,
            "P0" : P0 ,
            "Q_turbine_out":Q_turbine_out
            }
