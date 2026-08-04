import requests
import numpy as np
from CoolProp.CoolProp import PropsSI
from config import *
 
def get_temperature( long , lat ,year,months):
     try:
        append = ""
        if isinstance(year , tuple):
            append = f"&start={year[0]}&end={year[1]}"
        else:
            append = f"&start={year}&end={year}"

        d = requests.get(f"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M_MAX&community=SB&longitude={long}&latitude={lat}&format=JSON" + append)

        return (np.array(list(d.json()["properties"]["parameter"]["T2M_MAX"].values()))[np.array(months)-1] , 0)
     except:
         print("error in get request")
         return (None , 1)



def available_fluids():  
    global ORC_FLUIDS
    available_fluids = [] 
    for i in ORC_FLUIDS:
        for j in range(ORC_FLUIDS.index(i) + 1 , len(ORC_FLUIDS)):
            mixture = f"{thermodynamic_calculation_method}::{i}[0.5]&{ORC_FLUIDS[j]}[0.5]"
            try:
                PropsSI("D", "T", 300, "P", 101325, mixture)
                available_fluids.append(set((i , ORC_FLUIDS[j])))
            except:
                pass
    return available_fluids

# filter the fluid with mass fraction less than mixture_mass_fraction_limit
# remove the extra fluids with respect to n_fluid
def fil(a):
    b = a / a.sum()
    filtered_list =  np.array(list(map(lambda f: 0 if f < mixture_mass_fraction_limit else f , b)))
    # filtered_list = b[b > 1e-6]
    return filtered_list / sum(filtered_list)
def normalization(x):
    if x.ndim == 1:
        nth_biggest = np.argsort(x)[::-1][:n_fluids]
        zeros = np.zeros(x.shape)
        zeros[nth_biggest] = x[nth_biggest]
        return fil(zeros)
    else:    
        nth_biggest = np.argsort(x)[:,::-1][: , :n_fluids]
        zeros = np.zeros(x.shape)
        for i in range(len(nth_biggest)):
            for j in range(len(nth_biggest[i])):
                zeros[i][nth_biggest[i][j]] = x[i][j]
        return np.apply_along_axis(fil, 1 , zeros)