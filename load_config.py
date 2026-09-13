from dataclasses import dataclass
import json
import sys

config = None

@dataclass
class Config():
    run_name:str
    T0 : float  #default ambient temperature [C]
    city_location: list[float] | None #put None to use default ambient temperature
    T_source:float # heat source temperature [C]
    max_boiler_pressure :float #[pa]
    min_turbine_outlet_quality :float #[0-1]
    ORC_FLUIDS : list[str]
    cooling_temperature_difference :float #[C]
    condenser_pressure_drop:float #[pa]
    n_fluids: int|None # number of fluids that algorithm should make a mixture with
    max_n_fluids: int | None # algorithm can pick best fluid mixture for you [put -1 for none restricted fluid selection]
    should_minimize_n_fluids : bool
    #WARN :n_fluids and max_n_fluids are incompatible variables and one must be None at all time
    should_print_run :bool
    mixture_mass_fraction_limit: float 
    thermodynamic_calculation_method:str # [REFPROP | SRK | HEOS] use REFPROP if you have refprop installed 
    REFPROP_path:str
    n_run:int #how many times should the algorithm run
    n_gen:int 
    n_pop:int
    turbine_efficiency:float 
    pump_efficiency:float
    mass_flow_rate:float

def load_config(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        config = Config(**data)
        if config.max_n_fluids != None and config.n_fluids != None:
            raise ValueError("n_fluids and max_n_fluids are incompatible variables and one must be None at all time")
        return config

if len(sys.argv) != 2:
    raise ValueError("too many command line arguments")
config = load_config(sys.argv[1]) # load config from json file; address provided by command line argument