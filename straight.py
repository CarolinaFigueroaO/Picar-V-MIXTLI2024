from picar import back_wheels, front_wheels
import picar



picar.setup()
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()

fw.offset = 10


bw.speed = 20
bw.backward()

count = 0

while count < 100:
    count += 0.1
    print(count)
    if count > 50 and count < 60:
        fw.turn(40)
    

bw.stop()
print("done")