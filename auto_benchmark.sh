#!/usr/bin/env bash
# Automatically sets up environments and runs benchmarks for modin.

# sudo yum install git -y

STARTDIR="$PWD"
cd ..
if [ ! -d "modin" ]; then
    git clone https://github.com/noloerino/modin.git
fi
cd modin
git reset --hard origin/master
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
#TESTFLAGS="--profile-svg"

RESULTDIR="b_results/"
mkdir -p "$RESULTDIR"

echo "*** Running pandas benchmarks ***"
source "$BVENV/bin/activate"
pytest -k test_pandas $TESTFLAGS | tee "$RESULTDIR/pandas_results.txt"
deactivate

echo "*** Running baseline benchmarks ***"
source "$BVENV/bin/activate"
pytest -k test_modin $TESTFLAGS | tee "$RESULTDIR/baseline_results.txt"
deactivate

echo "*** Running benchmarks w/o stats ***"
source "$OVENV/bin/activate"
pytest -k test_modin --nostats $TESTFLAGS | tee "$RESULTDIR/nostats_results.txt"
deactivate

echo "*** Running benchmarks with stats ***"
source "$OVENV/bin/activate"
pytest -k test_modin $TESTFLAGS | tee "$RESULTDIR/withstats_results.txt"
deactivate

echo "*** Done ***"
