"""
Benchmarking stuff, slightly modified from
https://github.com/modin-project/df-bench/blob/master/benchmark/base_bench.py
"""

import os

# Original csv is about 70 MB
dup_counts = [1, 3, 10]
test_files = [(f"dup_{i}_" if i != 1 else "") + "fhv_tripdata_2021-07.csv" for i in dup_counts]

c_DOLocation = "DOLocationID"
c_dropoff_datetime = "dropoff_datetime"
c_PULocation = "PULocationID"

class BaseBenchmark:
    """
    All methods in this class should be shadowed in the subclass so the benchmark
    output is more descriptive - e.g. ``benchmark(_test_read_csv, file)`` should be
    called in the child by a function called ``test_modin_read_csv``.
    """

    # Handle for "pandas" module
    _lib = None

    @classmethod
    def setup_class(cls):
        for i, fn in zip(dup_counts, test_files):
            if not os.path.exists(fn):
                os.system(f"./repeat_csv.sh fhv_tripdata_2021-07.csv {i}")


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
