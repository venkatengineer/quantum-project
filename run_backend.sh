#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Preload libgomp for Qiskit Aer on Linux glibc systems
GOMP_LIB=$(ls /data/project/.venv/lib/python*/site-packages/qiskit_aer.libs/libgomp*.so* 2>/dev/null | head -n 1)
if [ -n "$GOMP_LIB" ]; then
    export LD_PRELOAD="$GOMP_LIB${LD_PRELOAD:+:$LD_PRELOAD}"
fi

export PYTHONPATH="$DIR/backend:$PYTHONPATH"

echo "Starting QuantumShield FastAPI Backend on http://0.0.0.0:8000..."
exec /data/project/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
