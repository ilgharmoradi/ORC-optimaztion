import csv
from config import *

def visualize():
    with open(f"results/{run_name}.csv") as file:
        datahandler = list(csv.reader(file))
        
        print(datahandler)
    pass

if __name__ == "__main__":
    visualize()