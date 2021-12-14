"""
Benchmarking stuff, slightly modified from
https://github.com/modin-project/df-bench/blob/master/benchmark/base_bench.py
"""

import gc
import os

import pytest

# Original csv is about 70 MB
TAXI_CSV = "fhv_tripdata_2021-07.csv"
# TAXI_CSV = "smaller_tripdata.csv"

# 39 MB
CREDITS_CSV = "tmdb_5000_credits.csv"
# 5.5 MB
MOVIES_CSV = "tmdb_5000_movies.csv"

def dup_counts(k):
    return {
        "taxi": [1, 3, 5, 10, 20, 30, 40] if pytest.conf["big"] else [1],
        "movie": [1, 3, 5, 10, 20, 30, 40, 50] if pytest.conf["big"] else [1, 3],
    }[k]

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

    # @classmethod
    # def setup_class(cls):
    #     for i, fn in zip(dup_counts, test_files):
    #         if not os.path.exists(fn):
    #             os.system(f"./repeat_csv.sh fhv_tripdata_2021-07.csv {i}")

    def _make_file(self, base_file, dup_count):
        assert isinstance(base_file, str)
        assert isinstance(dup_count, int)
        if dup_count == 1:
            fn = base_file
        else:
            fn = f"dup_{dup_count}_{base_file}"
        if not os.path.exists(fn):
            os.system(f"./repeat_csv.sh {base_file} {dup_count}")
        return fn
    
    def reference(self, fn):
        import pandas
        l = self._lib
        self._lib = pandas
        ref = fn()
        self._lib = l
        return ref
    
    @pytest.fixture(autouse=True)
    def gc(self):
        gc.collect()

    def _do_read_csv(self, file):
        df = self._lib.read_csv(file)
        # Force computation
        df.head()
        df.tail()
        return df

    # *** BEGIN notna ***
    # All "_do_.*" methods return the input df as well so it can be garbage collected
    def _do_notna_slow_order(self, file):
        df = self._lib.read_csv(file)
        return self._qp_notna_slow_order(df), df

    def _qp_notna_slow_order(self, df):
        dolocation = df[c_DOLocation]
        t1 = df[dolocation.notna()]
        pulocation = t1[c_PULocation]
        return t1[pulocation.notna()]

    def _do_notna_fast_order(self, file):
        df = self._lib.read_csv(file)
        return self._qp_notna_fast_order(df), df

    def _qp_notna_fast_order(self, df):
        pulocation = df[c_PULocation]
        t1 = df[pulocation.notna()]
        dolocation = t1[c_DOLocation]
        return t1[dolocation.notna()]
    # *** END notna ***

    # *** BEGIN comp ***
    def _do_comp_slow_order(self, file):
        df = self._lib.read_csv(file)
        return self._qp_comp_slow_order(df), df

    def _qp_comp_slow_order(self, df):
        t1 = df[df[c_DOLocation] > 100]
        # redundant comparison
        return t1[t1[c_DOLocation] > 200]

    def _do_comp_fast_order(self, file):
        df = self._lib.read_csv(file)
        return self._qp_comp_fast_order(df), df

    def _qp_comp_fast_order(self, df):
        dolocation = df[c_DOLocation]
        t1 = df[df[c_DOLocation] > 200]
        # redundant comparison
        return t1[t1[c_DOLocation] > 100]
    # *** END comp ***

    # *** BEGIN workflow ***
    def _do_workflow_slow_order(self, file):
        df = self._lib.read_csv(file)
        return self._qp_workflow_slow_order(df), df

    def _qp_workflow_slow_order(self, df):
        t1 = df[df[c_DOLocation].notna()]
        t2 = t1[t1[c_PULocation] > 100]
        return t2[c_PULocation].mean()

    def _do_workflow_fast_order(self, file):
        df = self._lib.read_csv(file)
        return self._qp_workflow_fast_order(df), df

    def _qp_workflow_fast_order(self, df):
        t1 = df[df[c_PULocation] > 100]
        t2 = df[df[c_DOLocation].notna()]
        return t2[c_PULocation].mean()
    # *** END workflow ***
