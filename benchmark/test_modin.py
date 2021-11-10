import pytest
import modin.pandas
from .base_bench import BaseBenchmark, test_files


class TestBenchmarkModin(BaseBenchmark):
    _lib = modin.pandas

    @pytest.mark.parametrize("file", test_files)
    def test_modin_read_csv(self, benchmark, file):
        benchmark(self._do_read_csv, file)

    @pytest.mark.parametrize("file", test_files)
    def test_modin_slow_order(self, benchmark, file):
        benchmark(self._do_notna_slow_order, file)

    @pytest.mark.parametrize("file", test_files)
    def test_modin_fast_order(self, benchmark, file):
        benchmark(self._do_notna_fast_order, file)
