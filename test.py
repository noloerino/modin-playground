import os
os.environ["MODIN_ENGINE"] = "ray"
import ray
ray.init()
import modin.pandas as pd

taxi_cab = pd.read_csv("fhv_tripdata_2021-07.csv")
dolocation = taxi_cab["DOLocationID"]
dolocation_not_na = taxi_cab[taxi_cab["DOLocationID"].notna()]

print(taxi_cab.shape)
