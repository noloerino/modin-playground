"""
Demonstrates the effects of running the same query multiple times.
Applied only to full tests.
"""
import pytest
import modin.pandas
import ray
ray.init(ignore_reinit_error=True)

from .base_bench import BaseBenchmark, TAXI_CSV, dup_counts

dataset = "taxi"
DATASET_CSV = TAXI_CSV
DUP_COUNTS = dup_counts(dataset)

import modin
is_lazy_modin = "+" in modin.__version__
opt_on = is_lazy_modin and not pytest.conf["nostats"]
if is_lazy_modin:
    from modin.core.storage_formats.pandas import stats_manager
    # Unlike test_modin, the function returns a concrete dataframe
    # this function also handles all the GC work
    def _wrap(fn):
        def run(lib, filename):
            df = lib.read_csv(filename)
            qc1 = fn(df)
            if not pytest.conf["nostats"]:
                stats_manager.compute_all() # optimizations are performed here
            result1 = qc1._plan.optimize().execute()
            # call again, which should hopefully use stats
            qc2 = fn(df)
            result2 = qc2._plan.optimize().execute()
            # for efficiency
            assert result1.shape == result2.shape
            del result1
            del result2
            del qc1
            del qc2
            del df
            stats_manager.clear_all()
        return run
else:
    def _wrap(fn):
        def run(lib, filename):
            df = lib.read_csv(filename)
            r1 = fn(df)
            r2 = fn(df)
            assert r1.shape == r2.shape
            del r1
            del r2
            del df
        return run


class TestBenchmarkModinDouble(BaseBenchmark):
    _lib = modin.pandas

    @pytest.fixture(params=DUP_COUNTS)
    def dup_count(self, request):
        return request.param

    # Forgot to run this with the rest, so here we are
    # technically it's not a double op lol
    def test_double_read_csv(self, benchmark, dup_count):
        file = self._make_file(DATASET_CSV, dup_count)
        benchmark(self._do_read_csv, file)

    def _do_double_full_test(self, qp_fn, benchmark, dup_count):
        file = self._make_file(DATASET_CSV, dup_count)
        benchmark(_wrap(qp_fn), self._lib, file)

    def test_double_full_notna_slow_order(self, benchmark, dup_count):
        self._do_double_full_test(self._qp_notna_slow_order, benchmark, dup_count)

    def test_double_full_notna_fast_order(self, benchmark, dup_count):
        self._do_double_full_test(self._qp_notna_fast_order, benchmark, dup_count)

    def test_double_full_comp_slow_order(self, benchmark, dup_count):
        self._do_double_full_test(self._qp_comp_slow_order, benchmark, dup_count)

    def test_double_full_comp_fast_order(self, benchmark, dup_count):
        self._do_double_full_test(self._qp_comp_fast_order, benchmark, dup_count)

    def test_double_full_workflow_slow_order(self, benchmark, dup_count):
        self._do_double_full_test(self._qp_workflow_slow_order, benchmark, dup_count)

    def test_double_full_workflow_fast_order(self, benchmark, dup_count):
        self._do_double_full_test(self._qp_workflow_fast_order, benchmark, dup_count)

