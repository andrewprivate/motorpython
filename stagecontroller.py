import serial
import time
import math

#change to current microstep
MICROVALUE = 1

STEPS_PER_MM = 200 * MICROVALUE / 2  # 200 steps per revolution, 32 microsteps, 2 mm per revolution
STEPS_PER_MM_Z = 200 * MICROVALUE / 10
MAX_STEPS_PER_COMMAND = 30000  # 16-bit unsigned integer, 2 bytes
HOME_AMOUNT_X = 350 * STEPS_PER_MM
HOME_AMOUNT_Y = 350 * STEPS_PER_MM
HOME_AMOUNT_Z = math.floor(600 * STEPS_PER_MM_Z)

class StageController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

        self.current_position = [0, 0, 0]
    
    def get_scale(self):
        return [STEPS_PER_MM, STEPS_PER_MM, STEPS_PER_MM_Z]


    def get_position(self):
        return self.current_position
    
    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)
            print("Connected to Arduino")
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")

    def read_message(self):
        if self.ser:
            return self.ser.readline().decode().strip()
        else:
            print("Serial connection not established.")
            return None

    def send_command(self, command):
        if self.ser:
            self.ser.write(command.encode())
        else:
            print("Serial connection not established.")
            return None

    def close(self):
        if self.ser:
            self.ser.close()
            print("Connection closed")

    def wait_until_done_moving(self):
        doneX = False
        doneY = False
        doneZ = False
        while True:
            message = self.read_message()
            # print(message)
            message = message[0] if message != None and message != "" else ""
            if message == 'x':
                doneX = True
            elif message == 'y':
                doneY = True
            elif message == 'z':
                doneZ = True
            else:
                pass

            if doneX and doneY and doneZ:
              #  print("Finished moving")
                break

    def moveBy(self, stepsX, stepsY, stepsZ, interval = 2, home = False):
        "Move the stage by the specified number of steps"

        if interval < 60:
            interval = 60
        
        directionX = '1' if stepsX < 0 else '0'
        directionY = '1' if stepsY < 0 else '0'
        directionZ = '1' if stepsZ < 0 else '0'

        stepsX = abs(stepsX)
        stepsY = abs(stepsY)
        stepsZ = abs(stepsZ)

        cycleX = math.floor(stepsX / MAX_STEPS_PER_COMMAND)
        cycleY = math.floor(stepsY / MAX_STEPS_PER_COMMAND)
        cycleZ = math.floor(stepsZ / MAX_STEPS_PER_COMMAND)

        remainderX = int(stepsX % MAX_STEPS_PER_COMMAND)
        remainderY = int(stepsY % MAX_STEPS_PER_COMMAND)
        remainderZ = int(stepsZ % MAX_STEPS_PER_COMMAND)

        home = '0' if home else '1'

        # Send the command to move the stage by the remainder
        commandX = f"a {remainderX} {directionX} {interval} {home} 0\n"
        commandY = f"a {remainderY} {directionY} {interval} {home} 1\n"
        commandZ = f"a {remainderZ} {directionZ} {interval * 2} {home} 2\n"

        self.send_command(commandX)
        self.send_command(commandY)
        self.send_command(commandZ)
        self.wait_until_done_moving()

        # Send the command to move the stage
        maxCycle = max(cycleX, cycleY, cycleZ)
        for i in range(maxCycle):
            # command: a [steps] [direction] [interval] [home] [motor]
            commandX = f"a {MAX_STEPS_PER_COMMAND if i < cycleX else 0} {directionX} {interval} {home} 0\n"
            commandY = f"a {MAX_STEPS_PER_COMMAND if i < cycleY else 0} {directionY} {interval} {home} 1\n"
            commandZ = f"a {MAX_STEPS_PER_COMMAND if i < cycleZ else 0} {directionZ} {interval * 2} {home} 2\n"
            self.send_command(commandX)
            self.send_command(commandY)
            self.send_command(commandZ)
            # Wait for the stage to finish moving before sending the next command.
            # Should recieve x, y, z, when the stage is done moving.
            self.wait_until_done_moving()
            
    
    def home(self, homeX = True, homeY = True, homeZ = True):
        "Move the stage to the home position"


        homeXSteps = -HOME_AMOUNT_X if homeX else 0
        homeYSteps = -HOME_AMOUNT_Y if homeY else 0
        homeZSteps = -HOME_AMOUNT_Z if homeZ else 0

        self.moveBy(homeXSteps, homeYSteps, homeZSteps, home=True)

        if homeX:
            self.current_position[0] = 0
        if homeY:
            self.current_position[1] = 0
        if homeZ:
            self.current_position[2] = 0

    def move_to(self, x, y, z, interval = 2):
        "Move the stage to the specified position in mm"

        moveX = x - self.current_position[0]
        moveY = y - self.current_position[1]
        moveZ = z - self.current_position[2]

        # Convert to steps
        moveX = math.floor(moveX * STEPS_PER_MM)
        moveY = math.floor(moveY * STEPS_PER_MM)
        moveZ = math.floor(moveZ * STEPS_PER_MM_Z)

        self.moveBy(moveX, moveY, moveZ, interval)
        
        # Update the current position
        self.current_position[0] += moveX / STEPS_PER_MM
        self.current_position[1] += moveY / STEPS_PER_MM
        self.current_position[2] += moveZ / STEPS_PER_MM_Z
 







        