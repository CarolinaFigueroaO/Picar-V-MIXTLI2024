from picar import back_wheels, front_wheels
import picar



picar.setup()
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()

fw.offset = 10


bw.speed = 0
bw.backward()
bw.speed = 30

count = 0

while count < 100:
    fw.turn(0)
    count += 0.00005

    

bw.stop()
print("done")