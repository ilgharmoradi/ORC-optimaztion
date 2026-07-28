from get_temperature_data import get_temperature
from CoolProp.CoolProp import PropsSI
import numpy as np

T0 = 20 + 273 #default ambient temperature

fluidLists = ["R134a" , "R22" ,"water"]

def calculate_thermodynamics(fluids , T_source : float , P_super_heat : float , mass_flow_rate : float = 1):
    global T0
    fluid_lists = list(fluids.keys())
    fluid_composition = list(fluids.values())
    P0 = PropsSI("P" , "T", T0 + 273.15, "Q" , 0 , fluid_lists[0])

    h1 = PropsSI("H" , "T", T0 + 273.15, "Q" , 0 , fluid_lists[0])
    s2 = PropsSI("S" , "T", T0 + 273.15, "Q" , 0 , fluid_lists[0])

    h2 = PropsSI("H" , "P", P_super_heat, "S" , s2 , fluid_lists[0])

    h3 = PropsSI("H" , "P", P_super_heat, "T" , T_source + 273.15, fluid_lists[0])
    s4 = PropsSI("S" , "P", P_super_heat, "T" , T_source +273.15, fluid_lists[0])

    h4 = PropsSI("H" , "P", P0, "S" , s4 , fluid_lists[0])

    w_turbine = abs(h3 - h4)
    w_pump = abs(h2 - h1)
    w_net = w_turbine - w_pump
    return w_net * mass_flow_rate

def main():
    global T0
    temperatures_at_Isfahan = get_temperature(51.6804 , 32.6613 , 2025 , (6 ,7 ,8))
    print("temperature of Isfahan city during summer:" , temperatures_at_Isfahan)
    T0 = np.sum(temperatures_at_Isfahan) / 3
    print(calculate_thermodynamics({"water" : 1} , 500 , 10e6))

if __name__ == '__main__':
    main()