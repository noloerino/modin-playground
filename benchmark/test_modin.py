import pytest
import modin.pandas
from .base_bench import BaseBenchmark, TAXI_CSV, CREDITS_CSV, MOVIES_CSV
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
        return lambda *args: fn(*args)._query_compiler._plan.execute_to_pandas()
    else:
        return fn


class TestBenchmarkModin(BaseBenchmark):
    _lib = modin.pandas

    #@pytest.mark.parametrize("file", test_files)
    #def test_modin_read_csv(self, benchmark, file):
    #    benchmark(self._do_read_csv, file)

    # """

    @pytest.mark.parametrize("dup_count", [1, 3])
    def test_modin_notna_slow_order(self, benchmark, dup_count):
        benchmark(_wrap(self._do_notna_slow_order), self._make_file(TAXI_CSV, dup_count))

    @pytest.mark.parametrize("dup_count", [1, 3])
    def test_modin_notna_fast_order(self, benchmark, dup_count):
        benchmark(_wrap(self._do_notna_fast_order), self._make_file(TAXI_CSV, dup_count))

    @pytest.mark.parametrize("dup_count", [1, 3, 5])
    def test_modin_ij_slow_order(self, benchmark, dup_count):
        benchmark(_wrap(self._do_ij_slow_order), self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count))

    @pytest.mark.parametrize("dup_count", [1, 3, 5])
    def test_modin_ij_fast_order(self, benchmark, dup_count):
        benchmark(_wrap(self._do_ij_fast_order), self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count))


if __name__ == "__main__":
    import modin.pandas as pd
    df = pd.read_csv("test")
    # Force computation
    df.head()
    df.tail()

