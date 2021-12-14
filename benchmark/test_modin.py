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
    """
    A '+' indicates that we pip installed from a local version of the repository.

    Our development version of modin returns a query plan rather than an actual
    dataframe, so we need to turn it into a pandas df object.
    """
    def _wrap(fn):
        def run(*args):
            qc, input_df = fn(*args)
            if not pytest.conf["nostats"]:
                stats_manager.compute_all() # optimizations are performed here
                result = qc._plan.optimize().execute()
                # in order to not interfere with test fixtures, make sure
                # full tests + test_compute_stats are run independent of other
                # component tests
            else:
                result = qc.execute()
            # even if optimizations are off, clear all to get rid of
            # memoized query plans
            stats_manager.clear_all()
            return result, input_df
        return run
else:
    def _wrap(fn):
        return fn


class TestBenchmarkModinOnce(BaseBenchmark):
    """
    Tests the results of running a benchmark where each query is run
    only a single time, that is, statistics are NOT reused between runs.
    """

    _lib = modin.pandas

    def eq_check(self, res, ref):
        # only check dimensions because there are bugs in read_csv with
        # heterogeneous data
        assert res.shape == ref.shape

    @pytest.fixture(params=DUP_COUNTS)
    def dup_count(self, request):
        return request.param

    def test_read_csv(self, benchmark, dup_count):
        file = self._make_file(DATASET_CSV, dup_count)
        benchmark(self._do_read_csv, file)

    # *** BEGIN FULL QUERY TESTS ***
    def _do_full_test(self, do_fn, benchmark, dup_count):
        file = self._make_file(DATASET_CSV, dup_count)
        result, input_df = benchmark(_wrap(do_fn), file)
        # for perf reasons, only check correctness for small duplicates
        if result.shape != (1, 1) and dup_count == 1:
            ref, ref_in = self.reference(lambda: do_fn(file))
            self.eq_check(result, ref)
            del ref
            del ref_in
        del result
        del input_df

    def test_full_notna_slow_order(self, benchmark, dup_count):
        self._do_full_test(self._do_notna_slow_order, benchmark, dup_count)

    def test_full_notna_fast_order(self, benchmark, dup_count):
        self._do_full_test(self._do_notna_fast_order, benchmark, dup_count)

    def test_full_comp_slow_order(self, benchmark, dup_count):
        self._do_full_test(self._do_comp_slow_order, benchmark, dup_count)

    def test_full_comp_fast_order(self, benchmark, dup_count):
        self._do_full_test(self._do_comp_fast_order, benchmark, dup_count)

    def test_full_workflow_slow_order(self, benchmark, dup_count):
        self._do_full_test(self._do_workflow_slow_order, benchmark, dup_count)

    def test_full_workflow_fast_order(self, benchmark, dup_count):
        self._do_full_test(self._do_workflow_fast_order, benchmark, dup_count)
    # *** END FULL QUERY TESTS ***

    # *** BEGIN FIXTURES ***
    # Because we have benchmarsk that run each stage of query planning separately,
    # these fixtures save us some redundant computation.

    @pytest.fixture
    def df_from_csv(self, dup_count):
        file = self._make_file(DATASET_CSV, dup_count)
        df = self._do_read_csv(file)
        if opt_on:
            stats_manager.compute_all()
        return df

    @pytest.fixture
    def notna_slow_plan_from_df(self, df_from_csv):
        return self._qp_notna_slow_order(df_from_csv)

    @pytest.fixture
    def notna_fast_plan_from_df(self, df_from_csv):
        return self._qp_notna_fast_order(df_from_csv)

    @pytest.fixture
    def comp_slow_plan_from_df(self, df_from_csv):
        return self._qp_comp_slow_order(df_from_csv)

    @pytest.fixture
    def comp_fast_plan_from_df(self, df_from_csv):
        return self._qp_comp_fast_order(df_from_csv)

    @pytest.fixture
    def workflow_slow_plan_from_df(self, df_from_csv):
        return self._qp_workflow_slow_order(df_from_csv)

    @pytest.fixture
    def workflow_fast_plan_from_df(self, df_from_csv):
        return self._qp_workflow_fast_order(df_from_csv)

    @pytest.fixture
    def notna_slow_optimized_from_plan(self, notna_slow_plan_from_df):
        if not is_lazy_modin:
            return None
        if opt_on:
            stats_manager.compute_all()
            return notna_slow_plan_from_df._plan.optimize()
        else:
            return notna_slow_plan_from_df._plan

    @pytest.fixture
    def notna_fast_optimized_from_plan(self, notna_fast_plan_from_df):
        if not is_lazy_modin:
            return None
        if opt_on:
            stats_manager.compute_all()
            return notna_fast_plan_from_df._plan.optimize()
        else:
            return notna_fast_plan_from_df._plan

    @pytest.fixture
    def comp_slow_optimized_from_plan(self, comp_slow_plan_from_df):
        if not is_lazy_modin:
            return None
        if opt_on:
            stats_manager.compute_all()
            return comp_slow_plan_from_df._plan.optimize()
        else:
            return comp_slow_plan_from_df._plan

    @pytest.fixture
    def comp_fast_optimized_from_plan(self, comp_fast_plan_from_df):
        if not is_lazy_modin:
            return None
        if opt_on:
            stats_manager.compute_all()
            return comp_fast_plan_from_df._plan.optimize()
        else:
            return comp_fast_plan_from_df._plan

    @pytest.fixture
    def workflow_slow_optimized_from_plan(self, workflow_slow_plan_from_df):
        if not is_lazy_modin:
            return None
        if opt_on:
            stats_manager.compute_all()
            return workflow_slow_plan_from_df._plan.optimize()
        else:
            return workflow_slow_plan_from_df._plan

    @pytest.fixture
    def workflow_fast_optimized_from_plan(self, workflow_fast_plan_from_df):
        if not is_lazy_modin:
            return None
        if opt_on:
            stats_manager.compute_all()
            return workflow_fast_plan_from_df._plan.optimize()
        else:
            return workflow_fast_plan_from_df._plan
    # *** END FIXTURES ***

    # *** BEGIN COMPONENT TESTS ***
    def skip_if_not_lazy(self):
        if "+" not in modin.__version__:
            pytest.skip("vanilla modin does not support stats/optimization")

    def skip_if_nostats(self):
        self.skip_if_not_lazy()
        if pytest.conf["nostats"]:
            pytest.skip("test configured to not collect stats")

    @pytest.mark.parametrize("dup_count", DUP_COUNTS)
    def test_full_compute_stats(self, benchmark, dup_count):
        """
        Not technically a full test, but should be run together with them
        to avoid gc effects with stats_manager.clear_all() interfering with
        other components.
        """
        self.skip_if_nostats()
        self._do_read_csv(self._make_file(DATASET_CSV, dup_count))
        benchmark(stats_manager.compute_next)
        assert stats_manager.size() == 0
        stats_manager.clear_all()

    def _do_qp_test(self, qp_fn, benchmark, df_from_csv):
        self.skip_if_nostats()
        stats_manager.compute_all()
        benchmark(lambda df: qp_fn(df), df_from_csv)
        stats_manager.clear_all()

    def test_p_notna_slow_qp(self, benchmark, df_from_csv):
        self._do_qp_test(self._qp_notna_slow_order, benchmark, df_from_csv)

    def test_p_notna_fast_qp(self, benchmark, df_from_csv):
        self._do_qp_test(self._qp_notna_fast_order, benchmark, df_from_csv)

    def test_p_comp_slow_qp(self, benchmark, df_from_csv):
        self._do_qp_test(self._qp_comp_slow_order, benchmark, df_from_csv)

    def test_p_comp_fast_qp(self, benchmark, df_from_csv):
        self._do_qp_test(self._qp_comp_fast_order, benchmark, df_from_csv)

    def test_p_workflow_slow_qp(self, benchmark, df_from_csv):
        self._do_qp_test(self._qp_workflow_slow_order, benchmark, df_from_csv)

    def test_p_workflow_fast_qp(self, benchmark, df_from_csv):
        self._do_qp_test(self._qp_workflow_fast_order, benchmark, df_from_csv)

    def _do_optimize_test(self, benchmark, qc):
        self.skip_if_nostats()
        benchmark(qc._plan.optimize)

    def test_p_notna_slow_optimize(self, benchmark, notna_slow_plan_from_df):
        self._do_optimize_test(benchmark, notna_slow_plan_from_df)

    def test_p_notna_fast_optimize(self, benchmark, notna_fast_plan_from_df):
        self._do_optimize_test(benchmark, notna_fast_plan_from_df)

    def test_p_comp_slow_optimize(self, benchmark, comp_slow_plan_from_df):
        self._do_optimize_test(benchmark, comp_slow_plan_from_df)

    def test_p_comp_fast_optimize(self, benchmark, comp_fast_plan_from_df):
        self._do_optimize_test(benchmark, comp_fast_plan_from_df)

    def test_p_workflow_slow_optimize(self, benchmark, workflow_slow_plan_from_df):
        self._do_optimize_test(benchmark, workflow_slow_plan_from_df)

    def test_p_workflow_fast_optimize(self, benchmark, workflow_fast_plan_from_df):
        self._do_optimize_test(benchmark, workflow_fast_plan_from_df)

    def _do_execute_test(self, benchmark, opt_plan):
        self.skip_if_not_lazy()
        df = benchmark(opt_plan.execute)
        del df

    def test_p_notna_slow_execute(self, benchmark, notna_slow_optimized_from_plan):
        self._do_execute_test(benchmark, notna_slow_optimized_from_plan)

    def test_p_notna_fast_execute(self, benchmark, notna_fast_optimized_from_plan):
        self._do_execute_test(benchmark, notna_fast_optimized_from_plan)

    def test_p_comp_slow_execute(self, benchmark, comp_slow_optimized_from_plan):
        self._do_execute_test(benchmark, comp_slow_optimized_from_plan)

    def test_p_comp_fast_execute(self, benchmark, comp_fast_optimized_from_plan):
        self._do_execute_test(benchmark, comp_fast_optimized_from_plan)

    def test_p_workflow_slow_execute(self, benchmark, workflow_slow_optimized_from_plan):
        self._do_execute_test(benchmark, workflow_slow_optimized_from_plan)

    def test_p_workflow_fast_execute(self, benchmark, workflow_fast_optimized_from_plan):
        self._do_execute_test(benchmark, workflow_fast_optimized_from_plan)
