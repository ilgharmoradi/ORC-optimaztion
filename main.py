from get_temperature_data import get_temperature
from CoolProp.CoolProp import PropsSI
import numpy as np


def main():
    temperatures_at_Isfahan = get_temperature(51.6804 , 32.6613 , 2025 , (6 ,7 ,8))
    print(temperatures_at_Isfahan)

if __name__ == '__main__':
    main()