import pytest
import pandas
from .base_bench import BaseBenchmark, TAXI_CSV, CREDITS_CSV, MOVIES_CSV


class TestBenchmarkPandas(BaseBenchmark):
    _lib = pandas

    # @pytest.mark.parametrize("file", test_files)
    # def test_pandas_read_csv(self, benchmark, file):
    #     benchmark(self._do_read_csv, file)

    @pytest.mark.parametrize("dup_count", [1, 3])
    def test_pandas_slow_order(self, benchmark, dup_count):
        benchmark(self._do_notna_slow_order, self._make_file(dup_count, TAXI_CSV))

    @pytest.mark.parametrize("dup_count", [1, 3])
    def test_pandas_fast_order(self, benchmark, dup_count):
        benchmark(self._do_notna_fast_order, self._make_file(dup_count, TAXI_CSV))

    @pytest.mark.parametrize("dup_count", [1, 3, 5])
    def test_pandas_ij_slow_order(self, benchmark, dup_count):
        benchmark(self._do_ij_slow_order, self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count))

    @pytest.mark.parametrize("dup_count", [1, 3, 5])
    def test_pandas_ij_fast_order(self, benchmark, dup_count):
        benchmark(self._do_ij_fast_order, self._make_file(CREDITS_CSV, dup_count), self._make_file(MOVIES_CSV, dup_count))
