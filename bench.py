#!/usr/bin/env python3

import gc
import os
import threading
import timeit

import multiprocessing

import ray
ray.init(num_cpus=multiprocessing.cpu_count() // 2) # Circumvent SMT
import modin.pandas as pd
import pandas as realpd

# The original taxicab CSV is about 70MB; both Modin and Pandas can do ops on a 250 GB frame but Pandas cannot transpose a 6GB frame efficiently
# Multiplying by 100 puts us at about 7GB
#dup_counts = [1, 3, 10, 50, 100, 500]
dup_counts = [1, 3, 10, 50, 70]
filenames = [(f"dup_{i}_" if i != 1 else "") + "fhv_tripdata_2021-07.csv" for i in dup_counts]
for i, fn in zip(dup_counts, filenames):
    if not os.path.exists(fn):
            os.system(f"./repeat_csv.sh fhv_tripdata_2021-07.csv {i}")
            # t = pd.read_csv("fhv_tripdata_2021-07.csv")

c_DOLocation = "DOLocationID"
c_dropoff_datetime = "dropoff_datetime"
c_PULocation = "PULocationID"

def order_one(df):
    # Filter DOLocationID first (probably slower?)
    dolocation = df[c_DOLocation]
    t1 = df[dolocation.notna()]
    pulocation = t1[c_PULocation]
    return t1[pulocation.notna()]

def order_two(df):
    # Filter PULocationID first (probably faster?)
    pulocation = df[c_PULocation]
    t1 = df[pulocation.notna()]
    dolocation = t1[c_DOLocation]
    return t1[dolocation.notna()]

def make_test_fn(pd_handle, csv_path, test_fn):
    df = pd_handle.read_csv(csv_path)
    return lambda: test_fn(df)

for fn in filenames:
    gc.collect()
    print("Timing order one on naive pandas with input", fn)
    print(timeit.timeit(make_test_fn(realpd, fn, order_one), number=10))

    gc.collect()
    print("Timing order one on modin with input", fn)
    print(timeit.timeit(make_test_fn(pd, fn, order_one), number=10))

    gc.collect()
    print("Timing order two on naive pandas with input", fn)
    print(timeit.timeit(make_test_fn(realpd, fn, order_two), number=10))

    gc.collect()
    print("Timing order two on modin with input", fn)
    print(timeit.timeit(make_test_fn(pd, fn, order_two), number=10))

