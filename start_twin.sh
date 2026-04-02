#!/bin/bash

echo "========================================"
echo " Starting E2CC Digital Twin Services... "
echo "========================================"


echo "[1/4] Starting Data Generator..."
python data_generator.py &
PID_GEN=$!


echo "[2/4] Starting Isolation Forest AI..."
python full_client.py &
PID_AI=$!


echo "[3/4] Starting RUL Calculator..."
python rul_days.py &
PID_RUL=$!


echo "[4/4] Starting React Dashboard..."

cd ui-dashboard
npm run dev &
PID_UI=$!

echo "========================================================"
echo " ALL SYSTEMS ONLINE "
echo " Dashboard is running at: http://localhost:5173"
echo " Press [CTRL + C] to safely shut down all services."
echo "========================================================"


trap "echo -e '\nShutting down all Digital Twin services...'; kill $PID_GEN $PID_AI $PID_RUL $PID_UI; exit" INT TERM


wait