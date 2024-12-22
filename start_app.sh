#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Bitcoin Trading Strategy Backtester...${NC}"

# Function to kill process on a specific port
kill_port_process() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        echo -e "${BLUE}Killing process on port $port...${NC}"
        fuser -k $port/tcp
        sleep 2
    fi
}

# Function to kill Python processes
kill_python_processes() {
    echo -e "${BLUE}Cleaning up Python processes...${NC}"
    pkill -f "python3 -m btc_trader.web.app"
    sleep 2
}

# Function to kill Node processes
kill_node_processes() {
    echo -e "${BLUE}Cleaning up Node processes...${NC}"
    pkill -f "node.*react-scripts start"
    sleep 2
}

# Clean up any existing processes
kill_python_processes
kill_node_processes
kill_port_process 3000
kill_port_process 5000

# Function to open browser based on OS
open_browser() {
    # Wait for a moment to ensure servers are ready
    sleep 5
    
    # Detect the operating system
    case "$(uname -s)" in
        Linux*)
            if command -v xdg-open &> /dev/null; then
                xdg-open http://localhost:3000
            elif command -v sensible-browser &> /dev/null; then
                sensible-browser http://localhost:3000
            else
                echo -e "${RED}Could not detect a browser launcher. Please open http://localhost:3000 manually.${NC}"
            fi
            ;;
        Darwin*)  # macOS
            open http://localhost:3000
            ;;
        CYGWIN*|MINGW*|MSYS*)  # Windows
            start http://localhost:3000
            ;;
        *)
            echo -e "${RED}Unknown operating system. Please open http://localhost:3000 manually.${NC}"
            ;;
    esac
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm and try again.${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd btc-trader-frontend
npm install
cd ..

# Start the backend server in the background
echo -e "${BLUE}Starting backend server...${NC}"
python3 -m btc_trader.web.app &
BACKEND_PID=$!

# Wait for backend to start and verify it's running
echo -e "${BLUE}Waiting for backend server to start...${NC}"
max_attempts=30
attempt=0
while ! curl -s http://localhost:5000 > /dev/null; do
    sleep 1
    ((attempt++))
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}Backend server failed to start. Retrying...${NC}"
        kill $BACKEND_PID 2>/dev/null
        sleep 2
        python3 -m btc_trader.web.app &
        BACKEND_PID=$!
        attempt=0
    fi
done

# Start the frontend development server
echo -e "${BLUE}Starting frontend development server...${NC}"
cd btc-trader-frontend
npm start &
FRONTEND_PID=$!

# Wait for frontend to start and verify it's running
echo -e "${BLUE}Waiting for frontend server to start...${NC}"
attempt=0
while ! curl -s http://localhost:3000 > /dev/null; do
    sleep 1
    ((attempt++))
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}Frontend server failed to start. Retrying...${NC}"
        kill $FRONTEND_PID 2>/dev/null
        sleep 2
        npm start &
        FRONTEND_PID=$!
        attempt=0
    fi
done

cd ..

# Launch browser in the background
open_browser &
BROWSER_PID=$!

# Function to handle script termination
cleanup() {
    echo -e "${BLUE}\nShutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $BROWSER_PID 2>/dev/null
    kill_python_processes
    kill_node_processes
    kill_port_process 3000
    kill_port_process 5000
    exit 0
}

# Function to restart services
restart_services() {
    echo -e "${BLUE}\nRestarting services...${NC}"
    
    # Kill existing processes
    cleanup
    
    # Start backend
    echo -e "${BLUE}Restarting backend server...${NC}"
    python3 -m btc_trader.web.app &
    BACKEND_PID=$!
    
    # Wait for backend
    sleep 3
    
    # Start frontend
    echo -e "${BLUE}Restarting frontend server...${NC}"
    cd btc-trader-frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}Services restarted!${NC}"
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Register restart function for USR1 signal
trap restart_services SIGUSR1

echo -e "${GREEN}Both services are running!${NC}"
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}Backend: http://localhost:5000${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo -e "${BLUE}Send SIGUSR1 signal to restart services (kill -USR1 $$)${NC}"

# Keep the script running
wait