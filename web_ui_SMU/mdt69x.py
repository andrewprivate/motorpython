import serial
import io
import threading

class RangeError(Exception):
    """Parameter out of range"""
    def __init__(self, message):
        self.message = message

class DeviceError(Exception):
    """Unsupported device"""
    def __init__(self, message):
        self.message = message

class Thorpezo():
    def __init__(self,dev):
        self.readresponse=True
        self.opencon(dev)
        self.info = self.msg('id?')
        self.closecon()
        try:
            if "MDT694B" in self.info[0]:
                self.device=MDT694B(dev)
            elif "MDT693B" in self.info[0]:
                self.device=MDT693B(dev)
            else:
                raise DeviceError
        except:
            print(self.info)
            
    def opencon(self,dev):
        self.ser = serial.Serial(port=dev,
                                 baudrate=115200,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=0.01)
        
        self.buf = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 33554432), newline='\r', line_buffering = True)
    
    def closecon(self):
        self.ser.close()

    def msg(self, msg):
        self.buf.write(msg+'\n')
        if self.readresponse:
            lines=self.buf.readlines()
            lines = [line.strip() for line in lines if not line.strip() == '']
            if lines[-1]=='>':
                lines = lines[:-1]
            return lines
        else:
            return ""

class PCbase():
    def __init__(self,dev):
        self.opencon(dev)
        self.readresponse=True
        self.ser_read_thread=threading.Thread(target=self.ser_read_thread)
        self.ser_read_thread.daemon=True
        self.ser_read_thread.start()

    def opencon(self,dev):
        self.ser = serial.Serial(port=dev,
                                 baudrate=115200,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=0.01)
        
        self.buf = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 33554432), newline='\r', line_buffering = True)
    
    def closecon(self):
        self.ser.close()
        
    def ignore_serial_read(self,ignore):
        self.readresponse= not ignore
    
    def ser_read_thread(self):
        while True:
            if not self.readresponse:
                line=self.buf.readline()

    def msg(self, msg):
        self.buf.write(msg+'\n')
        if self.readresponse:
            lines=self.buf.readlines()
            lines = [line.strip() for line in lines if not line.strip() == '']
            if lines[-1]=='>':
                lines = lines[:-1]
            return lines
        else:
            return ['']
    
    def get_commands(self):
        """List the available commands"""
        return self.msg('?')
    
    def get_info(self):
        """Returns the product header and firmware version """
        return self.msg('id?')
    
    def restore_factory_settings(self):
        """Restores default factory settings"""
        return self.msg('restore')
    
    def get_echo(self):
        """Returns echo status """
        return self.msg('echo?')
    
    def set_echo(self,enable):
        """Sets Echo mode. When the echo mode is on the command parameters will be returned, or echoed back, to the communication program. (Values: 1 = enable; 0 = disable)"""
        return self.msg('echo='+str(1 if enable else 0))
    
    def get_vlimit(self):
        """Returns output voltage limit setting. (75V = 0; 100V = 1; 150V = 2)"""
        return self.msg('vlimit?')
    
    def get_display_intensity(self):
        """Returns the display intensity"""
        return self.msg('intensity?')
    
    def set_display_intensity(self,intensity):
        """Set the Display Intensity (0-15)"""
        if intensity in range(0,16):
            return self.msg('intensity='+str(intensity))
        else:
            raise RangeError

    def get_xvolt(self):
        """Reads and returns the X axis output voltage"""
        return self.msg('xvoltage?')

    def set_xvolt(self,v):
        """Set the output voltage for the X axis"""
        return self.msg('xvoltage='+str(v))

    def get_xmin(self):
        """Reads the minimum output voltage limit for X axis"""
        return self.msg('xmin?')

    def set_xmin(self,v):
        """Sets the minimum output voltage limit for X axis"""
        return self.msg('xmin='+str(v))

    def get_xmax(self):
        """Reads and returns the maximum output voltage limit for X axis"""
        return self.msg('xmax?')

    def set_xmax(self,v):
        """Sets the maximum output voltage limit for X axis"""
        return self.msg('xmax='+str(v))
    
    def get_dacstep(self):
        """Reads the current step resolution"""
        return self.msg('dacstep?')
    
    def set_dacstep(self,step):
        """Sets the step resolution when using up/down arrow keys (n = 1 to 1000) """
        if step in range(1,1001):
            return self.msg('dacstep='+str(step))
        else:
            raise RangeError
        
    def get_name(self):
        """Returns the friendly name"""
        return self.msg('friendly?')
    
    def set_name(self,name):
        """Sets the friendly name"""
        return self.msg('friendly='+str(name))
    
    def get_sn(self):
        """Returns the serial number"""
        return self.msg('serial?')
    
    def get_compat_mode(self):
        """Returns compatibility mode (0 = disabled, 1 = enabled) """
        return self.msg('cm?')
    
    def set_compat_mode(self,enable):
        """Sets compatibility mode (0 = disable, 1 = enable)"""
        return self.msg('cm='+str(1 if enable else 0))
    
    def get_rot_mode(self):
        """Returns the rotary controls mode. (0 = Default, 1 = 10 turn pot, 2 = fine) """
        return self.msg('rotarymode?')
    
    def set_rot_mode(self,mode):
        """Sets the rotary controls mode. (0 = Default, 1 = 10 turn pot, 2 = fine) """
        if mode in [0, 1, 2]:
            return self.msg('rotarymode='+str(mode))
        else:
            raise RangeError
    
    def get_push_enabled(self):
        """Gets the disable rotary push to adjust requirement setting. (0 = push required, 1 = push not required) """
        return self.msg('pushdisable?')
    
    def set_push_enabled(self,enable):
        """Returns the disable rotary push to adjust requirement setting. (0 = push required, 1 = push not required) """
        return self.msg('pushdisable='+str(1 if enable else 0))
    
    
class MDT694B(PCbase):
    def get_sysmax(self):
        """Returns the maximum output voltage for the system"""
        return self.msg('sysmax?')
    
    def set_sysmax(self,v):
        """Sets the maximum output voltage for the system"""
        return self.msg('sysmax='+str(v))


class MDT693B(PCbase):
    def set_all_voltages(self,voltage):
        """Sets all outputs to desired voltage"""
        return self.msg('allvoltage='+str(voltage))
    
    def get_ms_enable(self):
        """Returns the state of the Master Scan enable"""
        return self.msg('msenable?')
    
    def set_ms_enable(self,enable):
        """Sets Master Scan mode. (Values: 1 = enable; 0 = disable)"""
        return self.msg('msenable='+str(1 if enable else 0))
    
    def get_ms_voltage(self):
        """Reads and Returns the master scan voltage"""
        return self.msg('msvoltage?')
    
    def get_ms_voltage(self,v):
        """Sets a master scan voltage that adds to the x, y, and z axis voltages. (Sets master scan DAC)"""
        return self.msg('msvoltage='+str(v))
    
    def get_yvolt(self):
        """Reads and returns the Y axis output voltage"""
        return self.msg('yvoltage?')
    
    def get_zvolt(self):
        """Reads and returns the Z axis output voltage"""
        return self.msg('zvoltage?')
    
    def set_yvolt(self,v):
        """Set the output voltage for the Y axis"""
        return self.msg('yvoltage='+str(v))
    
    def set_zvolt(self,v):
        """Set the output voltage for the Z axis"""
        return self.msg('zvoltage='+str(v))
    
    def get_ymin(self):
        """Reads the minimum output voltage limit for Y axis"""
        return self.msg('ymin?')
    
    def get_zmin(self):
        """Reads the minimum output voltage limit for Z axis"""
        return self.msg('zmin?')
    
    def set_ymin(self,v):
        """Sets the minimum output voltage limit for Y axis"""
        return self.msg('ymin='+str(v))
    
    def set_zmin(self,v):
        """Sets the minimum output voltage limit for Z axis"""
        return self.msg('zmin='+str(v))
    
    def get_ymax(self):
        """Reads and returns the maximum output voltage limit for Y axis"""
        return self.msg('ymax?')
    
    def get_zmax(self):
        """Reads and returns the maximum output voltage limit for Z axis"""
        return self.msg('zmax?')
    
    def set_ymax(self,v):
        """Sets the maximum output voltage limit for Y axis"""
        return self.msg('ymax='+str(v))
    
    def set_zmax(self,v):
        """Sets the maximum output voltage limit for Z axis"""
        return self.msg('zmax='+str(v))