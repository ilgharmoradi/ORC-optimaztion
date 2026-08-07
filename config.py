run_name = "run mod 4"
T0 = 40  #default ambient temperature [C]
T_source = 250 # heat source temperature [C]
max_boiler_pressure = 10e6 #[pa]
max_turbine_outlet_quality = 0.9 #[0-1]
ORC_FLUIDS = [
        "water",
        # Hydrofluorocarbons
        "R134a",
        "R143a",
        "R152A",
        "R227EA",
        "R236EA",
        "R236FA",
        "R245ca",
        "R245fa",
        "R365MFC",

        # Hydrofluoroolefins
        "R1233zd(E)",
        "R1234yf",
        "R1234ze(E)",
        "R1234ze(Z)",

        # Hydrochlorofluorocarbons
        "R123",
        "R124",
        "R141b",
        "R142b",
        "R22",

        # Hydrocarbons
        "n-Butane",
        "IsoButane",
        "n-Pentane",
        "IsoPentane",
        "Cyclopentane",
        "CycloHexane",
        "n-Hexane",
        "n-Heptane",
        "n-Octane",
        "Benzene",
        "Toluene",

        # Oxygenated compounds
        "Acetone",
        "Ethanol",
        "Methanol",

        # Specialty fluids
        "Novec649"
    ]
cooling_temperature_difference = 15 #[C]
n_fluids = 4 # number of fluids that algorithm should make a mixture with
max_n_fluids = None # algorithm can pick best fluid mixture for you [put -1 for none restricted fluid selection]
should_minimize_n_fluids = False
#WARN :n_fluids and max_n_fluids are incompatible variables and one must be None at all time
should_print_run = True
mixture_mass_fraction_limit = 1e-6 
thermodynamic_calculation_method = "REFPROP" # [REFPROP | SRK] use REFPROP if you have refprop installed 
REFPROP_path = r"C:\Program Files\REFPROP"
n_run = 1 #how many times should the algorithm run
n_gen = 80
n_pop = 40