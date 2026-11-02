#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

GOMP_LIB=$(ls /data/project/.venv/lib/python*/site-packages/qiskit_aer.libs/libgomp*.so* 2>/dev/null | head -n 1)
if [ -n "$GOMP_LIB" ]; then
    export LD_PRELOAD="$GOMP_LIB${LD_PRELOAD:+:$LD_PRELOAD}"
fi

export PYTHONPATH="$DIR/backend:$PYTHONPATH"

echo "=========================================="
echo "Running QuantumShield Backend PyTest Suite"
echo "=========================================="
/data/project/.venv/bin/pytest backend/tests -v

echo ""
echo "=========================================="
echo "Running QuantumShield Flutter Mobile Tests"
echo "=========================================="
cd flutter_app
/home/venkatengineer/development/flutter/bin/flutter test
/home/venkatengineer/development/flutter/bin/flutter analyze

echo ""
echo "All tests passed successfully!"
