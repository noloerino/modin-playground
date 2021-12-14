#!/usr/bin/env bash
# Automatically sets up environments and runs benchmarks for modin.

# sudo yum install git -y

STARTDIR="$PWD"
cd ..
if [ ! -d "modin" ]; then
    git clone https://github.com/noloerino/modin.git
fi
cd modin
git pull
cd "$STARTDIR"

echo "*** Creating virtual environments ***"

BVENV="baseline_venv"
OVENV="our_venv"
clean_install() {
    if [ -d "$BVENV" ]; then
        rm -rf "$BVENV"
    fi
    python3 -m venv "$BVENV"
    source "$BVENV/bin/activate"
    pip3 install -Iv "modin[ray]==0.11.3"
    pip3 install pytest pytest-benchmark pytest-profiling
    deactivate

    if [ -d "$OVENV" ]; then
        rm -rf "$OVENV"
    fi
    python3 -m venv "$OVENV"
    source "$OVENV/bin/activate"
    python3 -m pip install -e ../modin[ray]
    pip3 install pytest pytest-benchmark pytest-profiling
    deactivate
}

if [ ! -d "$BVENV" ] || [ ! -d "$OVENV" ]; then
    clean_install
fi

TESTFLAGS="--big"
# TESTFLAGS="--profile-svg"

RESULTDIR="b_results/"
mkdir -p "$RESULTDIR"

BENCH_CSVDIR="bench_csv/"
mkdir -p "$BENCH_CSVDIR"

do_test() {
    NAME=$1
    shift 1
    FLAGS=$@

    BENCH_JSONDIR="bench_json/$NAME"
    mkdir -p "$BENCH_JSONDIR"

    pytest -k test_double_ \
        --benchmark-storage="$BENCH_JSONDIR/double" \
        --benchmark-save="${NAME}" \
        $FLAGS

    py.test-benchmark --storage="$BENCH_JSONDIR/double" \
        compare --csv="$BENCH_CSVDIR/${NAME}_test_double"

    pytest -k test_full_ \
        --benchmark-storage="$BENCH_JSONDIR/full" \
        --benchmark-save="${NAME}" \
        $FLAGS

    py.test-benchmark --storage="$BENCH_JSONDIR/full" \
        compare --csv="$BENCH_CSVDIR/${NAME}_test_full"

    if [ "$NAME" != "baseline" ]; then
        pytest -k test_p_ \
            --benchmark-storage="$BENCH_JSONDIR/part" \
            --benchmark-save="${NAME}" \
            $FLAGS

        py.test-benchmark --storage="$BENCH_JSONDIR/part" \
            compare --csv="$BENCH_CSVDIR/${NAME}_test_part"
    fi

}

echo "*** Running baseline benchmarks ***"
source "$BVENV/bin/activate"
ray stop --force
do_test baseline $TESTFLAGS
deactivate

echo "*** Running benchmarks w/o stats ***"
source "$OVENV/bin/activate"
ray stop --force
do_test nostats $TESTFLAGS --nostats
deactivate

echo "*** Running benchmarks with stats ***"
source "$OVENV/bin/activate"
ray stop --force
do_test withstats $TESTFLAGS
deactivate

echo "*** Done ***"
