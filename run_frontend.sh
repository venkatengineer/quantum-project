#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Preload libgomp for Qiskit Aer
GOMP_LIB=$(ls /data/project/.venv/lib/python*/site-packages/qiskit_aer.libs/libgomp*.so* 2>/dev/null | head -n 1)
if [ -n "$GOMP_LIB" ]; then
    export LD_PRELOAD="$GOMP_LIB${LD_PRELOAD:+:$LD_PRELOAD}"
fi

export PYTHONPATH="$DIR/backend:$DIR/frontend:$DIR:$PYTHONPATH"

echo "Starting QuantumShield Streamlit Dashboard on http://localhost:8501..."
exec /data/project/.venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501 --server.headless true
