"""
Benchmarking stuff, slightly modified from
https://github.com/modin-project/df-bench/blob/master/benchmark/base_bench.py
"""

import os
import modin.pandas as pd
from modin.core.storage_formats.pandas import run_compute_stats
import numpy as np
import pandas
import ray
ray.init()

def reference():
    df = pandas.DataFrame({"c1": [0, 1, 2, 3, 4], "c2": [np.nan, np.nan, 1, 1, 1]})
    mask = df["c2"].notna()
    return df[mask]


if __name__ == "__main__":
    df = pd.DataFrame({"c1": [0, 1, 2, 3, 4], "c2": [np.nan, np.nan, 1, 1, 1]})

    run_compute_stats()

    col = df["c2"]
    mask = col.notna()
    result = df[mask]
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

