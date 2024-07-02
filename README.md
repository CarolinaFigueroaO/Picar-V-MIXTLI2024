# Tec Formula in Grand Prix Autonomous Mechatronics - May 2024

In this code, I developed an algorithm in Python for the Picar V car kits' autonomous driving, using the Picar library for motor control.

### Requirements for its use
- Picar V kit
- Picar library from the repository: 
    [git@github.com:sunfounder/SunFounder_PiCar-V.git](https://github.com/sunfounder/SunFounder_PiCar-V)
- OpenCV and numpy python libraries
- Real VNC server and viewer for the remote control


### Usage
This algorithm can be used on a circuit with black background, and the two lane lines are white (without midlines).

The static test video code helps adjust the beta, alpha, and other necessary parameters to achieve the clearest line detection.

The autonomous movement code enables the car to drive through the circuit until you press 'q' to exit the program.