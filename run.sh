#!/bin/bash
# Super simple launcher - asks what to do

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║      SC-Generator Launcher Menu           ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "1) Install (first time setup)"
echo "2) Start All (frontend + backend)"
echo "3) Start Backend Only"
echo "4) Start Frontend Only"
echo "5) View Logs"
echo "6) Update"
echo "7) Exit"
echo ""
read -p "Choose option (1-7): " choice

case $choice in
  1)
    bash install.sh
    ;;
  2)
    bash start-all.sh
    ;;
  3)
    source venv/bin/activate
    python3 app.py
    ;;
  4)
    npm start
    ;;
  5)
    tail -f /tmp/sc-logs/backend.log
    ;;
  6)
    bash setup.sh
    ;;
  7)
    echo "Goodbye!"
    exit 0
    ;;
  *)
    echo "Invalid option"
    ;;
esac
