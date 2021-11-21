import pytest
import modin.pandas
from .base_bench import BaseBenchmark, test_files
import ray
ray.init()


def _wrap(fn):
    return lambda file: fn(file)._query_compiler._plan.execute().to_pandas()


class TestBenchmarkModin(BaseBenchmark):
    _lib = modin.pandas

    #@pytest.mark.parametrize("file", test_files)
    #def test_modin_read_csv(self, benchmark, file):
    #    benchmark(self._do_read_csv, file)

    @pytest.mark.parametrize("file", test_files)
    def test_modin_slow_order(self, benchmark, file):
        benchmark(_wrap(self._do_notna_slow_order), file)

    @pytest.mark.parametrize("file", test_files)
    def test_modin_fast_order(self, benchmark, file):
        benchmark(_wrap(self._do_notna_fast_order), file)


if __name__ == "__main__":
    import modin.pandas as pd
    df = pd.read_csv("test")
    # Force computation
    df.head()
    df.tail()

