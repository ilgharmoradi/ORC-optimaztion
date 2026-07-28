import requests
import numpy as np

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