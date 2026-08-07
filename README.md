# ORC optimization

![Python](https://img.shields.io/badge/python-3.11-blue)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

Multi-objective optimization of organic Rankine cycle (ORC) for waste heat recovery specialized for Iranian steel industry in Isfahan city
NSGA2 genetic algorithm is used to determine optimal fluid mixture and cycle parameters during summer
(national grid peak load time)

---

## changing the algorithm and thermodynamics parameters

to ease algorithm and thermodynamics parameter changing a python file named `config.py` has been created. you can modify the parameters listed: _(not that the following list will be updated)_
|name of parameter|functionality|unit|
|---|------|---|
|`run_name`|created CSV file name|
|`T0`|default ambient temperature|C(deg)|
|`max_boiler_pressure`|maximum boiler pressure|P|
|`max_turbine_outlet_quality`|maximum allowed turbine outlet steam quality|between [0-1]|
|`ORC_FLUIDS`|list of fluids to be tested (all fluids must be supported by CoolProp backend)||
`cooling_temperature_difference`|temperature difference between ambient and condenser |

---

## how to run

to get started running the algorithm you must have a version of python installed then follow the instructions below

- clone / download the repo to your machine
- open the terminal on the main folder
- run `pip install -r requirements.txt` in your terminal
- after installing all the required packages run `python main.py`

developed by [Ilghar Moradi](https://github.com/ilgharmoradi) mechanical student at [AUT](https://www.linkedin.com/school/amirkabir-university-of-technology-tehran-polytechnic/)
