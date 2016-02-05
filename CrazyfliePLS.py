"""
HOW TO USE THIS FILE:

This text should be green, if you are reading it using IDLE, the Python IDE. It's green
because it's a "comment" added to the program. The computer totally ignores it. Most of
the green text in this file is a note left to help you understand what's going on.

Look below for the line that says "class Quadcopter": in it you will find two functions
definitions starting with the word "def". Those two functions are __init__ and _update.
The __init__ function is run one time at the beginning of the program. The _update function
is run 10 times per second to set the current state of the quadcopter.

Your mission, should you choose to accept it, is to add code to the _update function to set
up a flight path for the quadcopter. Your copter will fly for 10 seconds each time this
program is run.

"""

# Red text is a comment too, but usually shorter



###################################################
# CRITICAL STEP!! SET YOUR QUADCOPTER NUMBER HERE #
QUADCOPTER_NUMBER = 5
#                                                 # 
# The quadcopter number is printed on the bottom  #
# of each quadcopter, and is a number between 1   #
# and 10 (point the nose up to differentiate six  #
# and nine).                                      #
###################################################





# Don't change this unless you reset the firmware on the quadcopters too
BANDWIDTH = "2M" # others are "250K" and "1M"


# Leave these "import" lines alone, you need them
import sys
sys.path.append("lib")

import time
from threading import Thread


# If this import is failing, you are missing the "lib" directory containing the Crazyflie SDK.
# You can download the SDK from https://github.com/bitcraze/crazyflie-clients-python --
# if you are unfamiliar with Github, find the "Download ZIP" option on the right side of the
# screen. Unpack it, and copy the whole "lib" folder to wherever you have put this file.
import cflib.crtp
from cflib.crazyflie import Crazyflie


import logging
logging.basicConfig(level=logging.ERROR)

""" Map from quadcopter number to radio channel. There is no magic here, we just
    manually programmed each quadcopter to use these channels. """
channelForGroup = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]


class QuadcopterAltHold:
    def __init__(self, cf):
        self._roll = 0
        self._pitch = 0
        self._yawRate = 0
        self._altitude = 32767
        self._time = 0.0

    def updateQuadcopter (self, cf):
        cf.param.set_value("flightmode.althold","True")
        cf.commander.send_setpoint (self._roll,
                                    self._pitch,
                                    self._yawRate,
                                    self._altitude)

    def setRoll (self, roll):
        if (roll < -45):
            self._roll = -45
        elif (roll > 45):
            self._roll = 45
        else:
            self._roll = roll

    def setPitch (self, pitch):
        if (pitch < -45):
            self._pitch = -45
        elif (pitch > 45):
            self._pitch = 45
        else:
            self._pitch = pitch

    def setYawRate (self, yawRate):
        self._yawRate = yawRate

    def holdAltitude (self):
        self._altitude = 32767

    def shutdown (self, cf):
        cf.param.set_value("flightmode.althold","False")
        cf.commander.send_setpoint (0,0,0,0)
        cf.close_link()



    """
    NOTE: the multiplication by 8000 is arbitrary, to convert the units
          to something approximating meters per second. It is by no means
          exact, but saying increaseAltitude(1) should make the quadcopter
          go up by about 1 m/s.
    """

    def increaseAltitude (self, altitude):
        self._altitude = 32767 + (altitude*8000)

    def decreaseAltitude (self, altitude):
        self._altitude = 32767 - (altitude*8000)





























        

    """
    EDIT THIS FUNCTION

          |
          |
          |
          |
       \  |  /
        \ | /
         \|/
          V
    A function that is called 10 times per second """
    def _update (self, cf):
        self._time += 0.1

        # Other functions you can use:
        # self.setPitch ( X ) where X is in degrees
        # self.setRoll ( X )
        # self.setYawRate ( X )

        if self._time < 1.0:
            self.increaseAltitude(1) # Go up at 1 meter per second
        elif self._time < 2.0:
            self.holdAltitude() # Hold the current altitude
        elif self._time < 4.0:
            self.decreaseAltitude(0.5) # Land at about 1/2 meter per second
        else:
            self.shutdown(cf) # Shut down
            return

        self.updateQuadcopter(cf)















        
            

class Quadcopter:

    """ A function that is run once at the beginning """
    def __init__(self, cf):
        print "Setting everything to zero..."
        cf.commander.send_setpoint(0, 0, 0, 0)
        self._updateCallCounter = 0


    """
    EDIT THIS FUNCTION

          |
          |
          |
          |
       \  |  /
        \ | /
         \|/
          V

    A function that is called 10 times per second """
    def _update (self, cf):
        self._updateCallCounter += 1

        # An example program: you can change the numbers, and/or add more "elif" statements
        if (self._updateCallCounter < 10):
            print "Taking off"
            # Format is send_setpoint (Roll, Pitch, Yaw, Throttle)
            cf.commander.send_setpoint (0,0,0,30000)
        elif (self._updateCallCounter < 11):
            print "Hovering"
            # Spin in place for 2 seconds
            cf.commander.send_setpoint (0,0,200,30000)
        elif (self._updateCallCounter < 12):
            print "Landing"
            cf.commander.send_setpoint (0,0,0,30000)
        else:
            print "Off"
            cf.commander.send_setpoint(0, 0, 0, 0)














class Controller:
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""
    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print "Connecting to %s" % link_uri

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        # Do not hijack the calling thread!
        #self._quadcopter = Quadcopter (self._cf)
        
        print "Connected."
        self._quadcopter = QuadcopterAltHold (self._cf)
        Thread(target=self._run).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print "Connection to %s failed: %s" % (link_uri, msg)

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print "Connection to %s lost: %s" % (link_uri, msg)

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print "Disconnected from %s" % link_uri

    def _quality_updated(self, quality):
        if quality < 30:
            print "Low link quality: %s", quality

    def _run(self):
        print "Running..."
        current_time = 0
        self._cf.commander.send_setpoint (0,0,0,0);
        while current_time <= 5:
            print current_time
            self._quadcopter._update(self._cf)
            time.sleep(0.1)
            current_time += 0.1
        self._cf.close_link()
        print "Done."
        


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print "Scanning interfaces for Crazyflies..."
    available = cflib.crtp.scan_interfaces()
    print "Crazyflies found:"
    for i in available:
        print i[0]
        
    print "For quadcopter #%s, trying to connection to a radio on channel %s" % (QUADCOPTER_NUMBER, channelForGroup[QUADCOPTER_NUMBER])
    interface = "radio://0/" + `channelForGroup[QUADCOPTER_NUMBER]` + "/" + BANDWIDTH
    print "That means interface %s" % (interface)
    le = Controller (interface)
