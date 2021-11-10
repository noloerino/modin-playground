import pytest
import pandas
from .base_bench import BaseBenchmark, test_files


class TestBenchmarkPandas(BaseBenchmark):
    _lib = pandas

    @pytest.mark.parametrize("file", test_files)
    def test_pandas_read_csv(self, benchmark, file):
        benchmark(self._do_read_csv, file)

    @pytest.mark.parametrize("file", test_files)
    def test_pandas_slow_order(self, benchmark, file):
        benchmark(self._do_notna_slow_order, file)

    @pytest.mark.parametrize("file", test_files)
    def test_pandas_fast_order(self, benchmark, file):
        benchmark(self._do_notna_fast_order, file)
