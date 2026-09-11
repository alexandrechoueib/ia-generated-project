
This repository needs to add several external libraries
that can be dangerous you need to create an python environnement.

below the steps that you must follow in order to run 
the project in a safe zone.

sudo apt update
sudo apt install python3-full python3-venv

python3 -m venv ~/xai-env
source ~/xai-env/bin/activate

python -m pip install --upgrade pip
python -m pip install xai-sdk
