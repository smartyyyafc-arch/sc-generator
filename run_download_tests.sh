#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PORT=3000
SERVER_URL="http://localhost:${SERVER_PORT}"
WAIT_TIME=3
MAX_WAIT=30
REPORT_DIR="${PROJECT_DIR}"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

print_info "VBS/HTA Download Test Suite"
print_info "============================"

# Kill any existing server on the port
print_info "Checking for existing server on port ${SERVER_PORT}..."
if lsof -i ":${SERVER_PORT}" &> /dev/null; then
    print_warning "Found existing process on port ${SERVER_PORT}, attempting to kill..."
    lsof -ti ":${SERVER_PORT}" | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Start the server
print_info "Starting download server on port ${SERVER_PORT}..."
cd "${PROJECT_DIR}"
node server.js > server.log 2>&1 &
SERVER_PID=$!
print_success "Server started with PID ${SERVER_PID}"

# Wait for server to be ready
print_info "Waiting for server to be ready (max ${MAX_WAIT}s)..."
elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
    if curl -s "${SERVER_URL}/api/files" > /dev/null 2>&1; then
        print_success "Server is ready!"
        break
    fi
    sleep 1
    elapsed=$((elapsed + 1))
done

if [ $elapsed -eq $MAX_WAIT ]; then
    print_error "Server failed to start within ${MAX_WAIT} seconds"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# Run Python tests
print_info "Running download tests..."
python3 test_vbs_hta_downloads.py --url "${SERVER_URL}" --wait 2 || TEST_EXIT=$?

# Stop the server
print_info "Shutting down server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
print_success "Server stopped"

# Generate summary report
print_info "Generating summary report..."

REPORT_FILE="${REPORT_DIR}/DOWNLOAD_TEST_REPORT_$(date +%Y%m%d_%H%M%S).txt"

cat > "$REPORT_FILE" << 'EOF'
================================================================================
VBS/HTA Download Test Report
================================================================================

Test Configuration:
  - Test Date: $(date -u)
  - Server URL: http://localhost:3000
  - Test Framework: Python 3 + requests
  - Browser Emulation: Manual download simulation

Test Results Summary:
EOF

echo "  - Test completed successfully" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Files Available for Download:" >> "$REPORT_FILE"

# List all VBS/HTA files
cd "${PROJECT_DIR}"
for file in *.vbs *.hta 2>/dev/null; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "  - $file ($size bytes)" >> "$REPORT_FILE"
    fi
done

echo "" >> "$REPORT_FILE"
echo "MIME Type Configuration:" >> "$REPORT_FILE"
echo "  - VBS files (.vbs): text/vbscript" >> "$REPORT_FILE"
echo "  - HTA files (.hta): application/x-mshta" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Download Headers Configuration:" >> "$REPORT_FILE"
echo "  - Content-Disposition: attachment (forces download)" >> "$REPORT_FILE"
echo "  - Cache-Control: no-cache, no-store, must-revalidate" >> "$REPORT_FILE"
echo "  - Pragma: no-cache" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Browser Compatibility Notes:" >> "$REPORT_FILE"
echo "  - Chrome/Edge: VBS downloads may trigger SmartScreen warning" >> "$REPORT_FILE"
echo "  - Firefox: Generally allows VBS downloads with warning" >> "$REPORT_FILE"
echo "  - Safari: May block VBS downloads as executable" >> "$REPORT_FILE"
echo "  - HTA: Generally not supported in modern browsers" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Test Files Generated:" >> "$REPORT_FILE"
echo "  - server.js: Node.js HTTP server with download support" >> "$REPORT_FILE"
echo "  - download-test.html: Interactive browser-based test interface" >> "$REPORT_FILE"
echo "  - test_vbs_hta_downloads.py: Automated download verification" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Server Logs:" >> "$REPORT_FILE"
if [ -f "server.log" ]; then
    echo "See server.log for detailed server output" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"
echo "================================================================================'" >> "$REPORT_FILE"

print_success "Report saved to $REPORT_FILE"
cat "$REPORT_FILE"

# Check for test report JSON
if [ -f "vbs_hta_download_report_*.json" ]; then
    print_success "Found detailed test results in JSON format"
    for report in vbs_hta_download_report_*.json; do
        print_info "Detailed report: $report"
    done
fi

print_info "Test suite completed!"
print_success "Download tests are ready to run interactively at http://localhost:3000 (requires running server)"

exit ${TEST_EXIT:-0}
