#!/usr/bin/env bash
# TruthStream backend test runner
# Usage: ./run_tests.sh [unit|integration|check]

set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

case "${1:-unit}" in
  unit)
    echo "Running unit tests (pytest)..."
    python -m pytest tests/ -v
    ;;
  integration)
    echo "Running integration test..."
    python integration_test.py
    ;;
  check)
    echo "Health check (requires server on port 8000 or 8001)..."
    for port in 8001 8000; do
      if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$port/health" 2>/dev/null | grep -q 200; then
        echo "OK: http://127.0.0.1:$port/health"
        exit 0
      fi
    done
    echo "No server responded on 8000/8001"
    exit 1
    ;;
  *)
    echo "Usage: $0 {unit|integration|check}"
    exit 1
    ;;
esac
