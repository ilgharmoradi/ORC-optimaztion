import requests
import numpy as np
from CoolProp.CoolProp import PropsSI
from math import floor
from load_config import config 

def get_temperature( location ,year,months):
     long , lat = location
     try:
        append = ""
        if isinstance(year , tuple):
            append = f"&start={year[0]}&end={year[1]}"
        else:
            append = f"&start={year}&end={year}"

        d = requests.get(f"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M_MAX&community=SB&longitude={long}&latitude={lat}&format=JSON" + append , timeout=3)

        return (np.array(list(d.json()["properties"]["parameter"]["T2M_MAX"].values()))[np.array(months)-1] , 0)
     except:
         print("error in get request")
         return (None , 1)



def available_fluids():  
    available_fluids = [] 
    for i in config.ORC_FLUIDS:
        for j in range(config.ORC_FLUIDS.index(i) + 1 , len(config.ORC_FLUIDS)):
            mixture = f"{config.thermodynamic_calculation_method}::{i}[0.5]&{config.ORC_FLUIDS[j]}[0.5]"
            try:
                PropsSI("D", "T", 300, "P", 101325, mixture)
                available_fluids.append(set((i , config.ORC_FLUIDS[j])))
            except:
                pass
    return available_fluids

# filter the fluid with mass fraction less than mixture_mass_fraction_limit
# remove the extra fluids with respect to n_fluid
def fil(a):
    b = a / a.sum()
    filtered_list =  np.array(list(map(lambda f: 0 if f < config.mixture_mass_fraction_limit else f , b)))
    # filtered_list = b[b > 1e-6]
    return filtered_list / sum(filtered_list)
def normalization(x , n = None):
    if config.n_fluids:
        n = config.n_fluids
    if x.ndim == 1:
        nth_biggest = np.argsort(x)[::-1][:n]
        zeros = np.zeros(x.shape)
        zeros[nth_biggest] = x[nth_biggest]
        return fil(zeros)

def normalize_k(x):
    if config.max_n_fluids == 1:
        return 1
    return floor(x * (config.max_n_fluids) + 1)