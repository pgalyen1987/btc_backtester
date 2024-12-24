#!/bin/bash

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to open browser
open_browser() {
    sleep 2  # Wait for server to be ready
    if command -v xdg-open >/dev/null; then
        xdg-open http://localhost:3000
    elif command -v open >/dev/null; then
        open http://localhost:3000
    else
        echo "Could not detect the web browser to use."
    fi
}

# Kill any existing processes on ports 5000 and 3000
echo "Cleaning up existing processes..."
if check_port 5000; then
    kill $(lsof -t -i:5000) 2>/dev/null || true
fi
if check_port 3000; then
    kill $(lsof -t -i:3000) 2>/dev/null || true
fi

# Wait for ports to be free
sleep 2

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend
echo "Starting backend server..."
cd "$(dirname "$0")"
python3 -m btc_trader.app > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..30}; do
    if check_port 5000; then
        echo "Backend started successfully"
        break
    fi
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo "Backend failed to start. Check logs/backend.log for details"
        exit 1
    fi
    sleep 1
done

# Start frontend
echo "Starting frontend..."
cd btc-trader-frontend
npm install > ../logs/frontend_install.log 2>&1
BROWSER=none npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
for i in {1..30}; do
    if check_port 3000; then
        echo "Frontend started successfully"
        break
    fi
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo "Frontend failed to start. Check logs/frontend.log for details"
        exit 1
    fi
    sleep 1
done

echo "Application started successfully!"
echo "Backend running on http://localhost:5000"
echo "Frontend running on http://localhost:3000"

# Open browser in background
open_browser &

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID