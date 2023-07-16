#! /bin/bash
set -e

echo "Executing: pip install virtualenv"
python3 -m pip install virtualenv

echo "Checking venv/"
if [ ! -d "venv" ] 
then
    echo "venv/ not found, creating..."
    python3 -m virtualenv venv
fi

echo "Entering venv/"
source ./venv/bin/activate

echo "Executing: pip insrall -r requirements.txt"
python3 -m pip install -r requirements.txt

echo "Starting pda"
python3 hta
