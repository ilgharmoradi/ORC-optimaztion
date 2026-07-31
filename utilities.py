import requests
import numpy as np
from CoolProp.CoolProp import PropsSI

def get_temperature( long , lat ,year,months) :
     try:
        append = ""
        if isinstance(year , tuple):
            append = f"&start={year[0]}&end={year[1]}"
        else:
            append = f"&start={year}&end={year}"

        d = requests.get(f"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M_MAX&community=SB&longitude={long}&latitude={lat}&format=JSON" + append)

        return np.array(list(d.json()["properties"]["parameter"]["T2M_MAX"].values()))[np.array(months)-1]
     except:
         print("error in get request")
         return 0

def available_fluids():  
    ORC_FLUIDS = [
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

    available_fluids = set() 
    for i in ORC_FLUIDS:
        for j in range(ORC_FLUIDS.index(i) + 1 , len(ORC_FLUIDS)):
            mixture = f"HEOS::{i}[0.5]&{ORC_FLUIDS[j]}[0.5]"
            try:
                PropsSI("D", "T", 300, "P", 101325, mixture)
                available_fluids.add(set([i , ORC_FLUIDS[j]]))
            except:
                pass
    return available_fluids