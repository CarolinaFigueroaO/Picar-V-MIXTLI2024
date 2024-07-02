# Tec Formula in Grand Prix Autonomous Mechatronics - May 2024

In this code, I developed an algorithm in Python for the Picar V car kits' autonomous driving, using the Picar library for motor control.

### Requirements for its use
- Picar V kit
- Picar library from the repository: 
    [git@github.com:sunfounder/SunFounder_PiCar-V.git](https://github.com/sunfounder/SunFounder_PiCar-V)
- Real VNC server and viewer


### Installation steps
1. Assemble your Picar V car.
2. Perform the basic configuration, such as setting up the username and password.
3. Clone the SunFounder Picar V repository.
4. Navigate to the repository directory on your Raspberry Pi.
5. Enter the following commands in the terminal:
sudo ./install_dependecies
picar servo-install


### Usage
This algorithm can be used on a circuit where the background is black, and the lane lines are white.

The static test video code helps adjust the beta, alpha, and other necessary parameters to achieve the clearest line detection.

The autonomous movement code enables the car to drive through the circuit until you press 'q' to exit the program.