##### Robo-cat project

The cat robot based on raspberry pi and pca9685 16 channel pwm board.

Now this is a first alpha version, just for test the hardware.

We use modified ServoPi library from here (ServoPi.py file):
https://github.com/abelectronicsuk/ABElectronics_Python_Libraries

keyboard module is used for control, so it requires root privileges

for dev install we need prepare environment on raspberry pi:
```bash
sudo apt-get update
sudo apt-get install -y git net-tools wget curl python3 python3-venv python3-pip mc
mkdir catty-venv
python3 -m venv ~/catty-venv
cd ~/catty-venv/
 . bin/activate
pip3 install smbus2 keyboard RPi.GPIO
```

and download the project
```bash
git clone https://github.com/eugenosm/robo-cat.git
```

the main file is `catty.py`
usage:
```bash
sudo python3 catty.py play 
 start robot and control it with 'wsad'. exit is '~' key
 
python3 catty.py adjust <channel> <position>
 for diagnostic/adjust pourpose we can set any of 16 servos to any position
 channel - 1..16
 position 0..180 degree  
```