from picar import back_wheels, front_wheels
import picar



picar.setup()
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()
fw.offset = 10
fw.turn(90)

bw.speed = 0
bw.backward()

bw.speed = 50
while True:
    pass

