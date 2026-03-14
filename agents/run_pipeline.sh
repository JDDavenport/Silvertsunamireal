#!/bin/bash
# ACQUISITOR Pipeline Brain Runner
# Usage: ./run_pipeline.sh [init|run|phase|health|summary]

cd "$(dirname "$0")/.."

COMMAND=${1:-run}
PHASE=$2

if [ "$COMMAND" = "phase" ] && [ -n "$PHASE" ]; then
    python3 agents/pipeline_brain.py phase --phase "$PHASE"
else
    python3 agents/pipeline_brain.py "$COMMAND"
fi
