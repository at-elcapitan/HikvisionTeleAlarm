#! /bin/bash
set -e
echo "Checking venv..."
if [ ! -d "venv" ] 
then
    echo "venv not found, creating..."
    python3 -m venv venv
fi

echo "Entering venv..."
source ./venv/bin/activate

echo "Entered venv."

echo "Running pip3"
pip3 install -r requirements.txt

echo "Done, running pda..."
python3 pda
