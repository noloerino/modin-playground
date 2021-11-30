"""
Benchmarking stuff, slightly modified from
https://github.com/modin-project/df-bench/blob/master/benchmark/base_bench.py
"""

import os
import modin.pandas as pd
import pandas
import ray
ray.init()

# Original csv is about 70 MB
dup_counts = [1, 3, 10]
test_files = [(f"dup_{i}_" if i != 1 else "") + "fhv_tripdata_2021-07.csv" for i in dup_counts]

c_DOLocation = "DOLocationID"
c_dropoff_datetime = "dropoff_datetime"
c_PULocation = "PULocationID"

class Scratch:
    _lib = pd

    def __init__(self):
        pass

    def _do_read_csv(self, file):
        df = self._lib.read_csv(file)
        # Force computation
        df.head()
        df.tail()

    def _do_notna_slow_order(self, file):
        df = self._lib.read_csv(file)
        dolocation = df[c_DOLocation]
        t1 = df[dolocation.notna()]
        pulocation = t1[c_PULocation]
        return t1[pulocation.notna()]

    def _do_notna_fast_order(self, file):
        df = self._lib.read_csv(file)
        pulocation = df[c_PULocation]
        t1 = df[pulocation.notna()]
        dolocation = t1[c_DOLocation]
        return t1[dolocation.notna()]

def reference():
    df = pandas.read_csv(test_files[0])
    dolocation = df[c_DOLocation]
    do_notna_mask = dolocation.notna()
    t1 = df[do_notna_mask]
    pulocation = t1[c_PULocation]
    return t1[pulocation.notna()]


if __name__ == "__main__":
    df = pd.read_csv(test_files[2])
    pulocation = df[c_PULocation]
    t1 = df[pulocation.notna()]
    dolocation = t1[c_DOLocation]
    result = t1[dolocation.notna()]
    #result.describe()
    print(result._query_compiler._plan)
    d = result._query_compiler._plan.execute_to_pandas().describe()
    print(d)
    """
    # TODO read_csv should also be deferable
    df = pd.read_csv(test_files[0])
    dolocation = df[c_DOLocation]
    # print("type(dolocation)=", type(dolocation))
    #print("dolocation..plan=", dolocation._query_compiler._plan.pretty_str())
    #print()
    do_notna_mask = dolocation.notna()
    #result = do_notna_mask
    #print("do_notna_mask..plan=", do_notna_mask._query_compiler._plan.pretty_str())
    #print()
    t1 = df[do_notna_mask]
    pulocation = t1[c_PULocation]
    #print("pulocation..plan=", pulocation._query_compiler._plan.pretty_str())
    pu_notna_mask = pulocation.notna()
    #print("pu_notna_mask..plan=", pu_notna_mask._query_compiler._plan.pretty_str())
    # TODO consider caching intermediate query compilers? t1 is used to compute pu_notnamask as well
    result = t1[pu_notna_mask]
    #print("result..plan=", result._query_compiler._plan.pretty_str())
    print("*** resolving full plan: ***")
    plan = result._query_compiler._plan
    print(plan.pretty_str())
    executed = plan.execute().to_pandas()
    print()
    print("*** REFERENCE ***")
    ref = reference()
    print(ref.head())
    print(ref.describe())
    print()
    print("*** ACTUAL ***")
    print(executed.head())
    print(executed.describe())
    """

