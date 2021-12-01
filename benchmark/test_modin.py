import pytest
import modin.pandas
from .base_bench import BaseBenchmark, TAXI_CSV, CREDITS_CSV, MOVIES_CSV, dup_counts
import ray
ray.init()

def _wrap(fn):
    import modin
    if "+" in modin.__version__:
        """
        A '+' indicates that we pip installed from a local version of the repository.

        Our development version of modin returns a query plan rather than an actual
        dataframe, so we need to turn it into a pandas df object.
        """
        def run(*args):
            from modin.core.storage_formats.pandas import stats_manager
            plan = fn(*args)._query_compiler._plan
            if not pytest.conf["nostats"]:
                stats_manager.compute_all()
                result = plan.optimize().execute()
                stats_manager.clear_all()
            else:
                result = plan.execute()
            return result
        return run
    else:
        return fn


class TestBenchmarkModin(BaseBenchmark):
    _lib = modin.pandas

    #@pytest.mark.parametrize("file", test_files)
    #def test_modin_read_csv(self, benchmark, file):
    #    benchmark(self._do_read_csv, file)

    # """
    def eq_check(self, res, ref):
        # only check dimensions because there are bugs in read_csv with
        # heterogeneous data
        assert res.shape == ref.shape
    
    @pytest.mark.parametrize("dup_count", dup_counts("taxi"))
    def test_modin_notna_slow_order(self, benchmark, dup_count):
        result = benchmark(_wrap(self._do_notna_slow_order), self._make_file(TAXI_CSV, dup_count))
        # only check correctness for small duplicates
        if dup_count == 1:
            ref = self.reference(lambda: self._do_notna_slow_order(self._make_file(TAXI_CSV, dup_count)))
            self.eq_check(result, ref)

    @pytest.mark.parametrize("dup_count", dup_counts("taxi"))
    def test_modin_notna_fast_order(self, benchmark, dup_count):
        result = benchmark(_wrap(self._do_notna_fast_order), self._make_file(TAXI_CSV, dup_count))
        # only check correctness for small duplicates
        if dup_count == 1:
            ref = self.reference(lambda: self._do_notna_fast_order(self._make_file(TAXI_CSV, dup_count)))
            self.eq_check(result, ref)
            
    @pytest.mark.parametrize("dup_count", dup_counts("taxi"))
    def test_modin_comp_slow_order(self, benchmark, dup_count):
        result = benchmark(_wrap(self._do_comp_slow_order), self._make_file(TAXI_CSV, dup_count))
        # only check correctness for small duplicates
        if dup_count == 1:
            ref = self.reference(lambda: self._do_comp_slow_order(self._make_file(TAXI_CSV, dup_count)))
            self.eq_check(result, ref)
    
    @pytest.mark.parametrize("dup_count", dup_counts("taxi"))
    def test_modin_comp_fast_order(self, benchmark, dup_count):
        result = benchmark(_wrap(self._do_comp_fast_order), self._make_file(TAXI_CSV, dup_count))
        # only check correctness for small duplicates
        if dup_count == 1:
            ref = self.reference(lambda: self._do_comp_fast_order(self._make_file(TAXI_CSV, dup_count)))
            self.eq_check(result, ref)

    # @pytest.mark.parametrize("dup_count", dup_counts("movie"))
    # def test_modin_ij_slow_order(self, benchmark, dup_count):
    #     result = benchmark(_wrap(self._do_ij_slow_order), self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count))
    #     # only check correctness for small duplicates
    #     # due to bugs in read_csv with heterogeneous data, we only check dimensions
    #     if dup_count == 1:
    #         ref = self.reference(lambda: self._do_ij_slow_order(self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count)))
    #         self.eq_check(result, ref)

    # @pytest.mark.parametrize("dup_count", dup_counts("movie"))
    # def test_modin_ij_fast_order(self, benchmark, dup_count):
    #     result = benchmark(_wrap(self._do_ij_fast_order), self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count))
    #     if dup_count == 1:
    #         ref = self.reference(lambda: self._do_ij_fast_order(self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count)))
    #         self.eq_check(result, ref)
    
    @pytest.mark.parametrize("dup_count", dup_counts("taxi"))
    def test_modin_compute_stats(self, benchmark, dup_count):
        import modin
        if "+" in modin.__version__:
            from modin.core.storage_formats.pandas import stats_manager
            self._do_read_csv(self._make_file(TAXI_CSV, dup_count))
            benchmark(stats_manager.compute_all)


if __name__ == "__main__":
    import modin.pandas as pd
    df = pd.read_csv("test")
    # Force computation
    df.head()
    df.tail()

