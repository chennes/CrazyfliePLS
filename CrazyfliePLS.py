"""
HOW TO USE THIS FILE:

This text should be green if you are reading it using IDLE, the Python IDE.
It's green because it's a "comment" added to the program. The computer totally
ignores it. Most of the green text in this file is a note left to help you
understand what's going on.

Look below for the line that says "class Quadcopter": in it you will
find two functions definitions starting with the word "def". Those two
functions are __init__ and _update. The __init__ function is run one time at
the beginning of the program. The _update function is run 10 times per second
to set the current state of the quadcopter.

Your mission, should you choose to accept it, is to add code to the _update
function to set up a flight path for the quadcopter. Your copter will fly for
10 seconds each time this program is run.

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

import time
from threading import Thread


# If this import is failing, you are missing the "crazyflie-lib-python/cflib" directory 
# containing the Crazyflie SDK.
# You can clone the SDK from https://github.com/bitcraze/crazyflie-lib-python
sys.path.append("crazyflie-lib-python/")
import cflib.crtp
from cflib.crazyflie import Crazyflie


import logging
logging.basicConfig(level=logging.ERROR)

""" Map from quadcopter number to radio channel. There is no magic here, we just
    manually programmed each quadcopter to use these channels. """
channelForGroup = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]















class Quadcopter:

    """ A function that is run once at the beginning """
    def __init__(self, cf):
        print ("Setting everything to zero...")
        cf.commander.send_setpoint(0, 0, 0, 0)
        self._time= 0


    def _update (self, cf):

        # An example program: you can change the numbers, and/or add more "elif" statements
        if (self._time < 0.7):
            # Format is send_setpoint (Roll, Pitch, Yaw rate, Throttle)
            cf.commander.send_setpoint (0,0,0,30000)
        elif (self._time < 1.5):
            # Spin in place (yaw rate = 200) 
            cf.commander.send_setpoint (0,0,200,30000)
        elif (self._updateCallCounter < 2.0):
	    # Land (sort of)
            cf.commander.send_setpoint (0,0,0,25000)
        else:
	    # Shut it all down
            cf.commander.send_setpoint(0, 0, 0, 0)

        self._time += 0.1














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

        print ("Connecting to %s" % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        
        print ("Connected.")
        self._quadcopter = Quadcopter (self._cf)
        Thread(target=self._run).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print ("Connection to %s failed: %s" % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print ("Connection to %s lost: %s" % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print ("Disconnected from %s" % link_uri)

    def _quality_updated(self, quality):
        if quality < 30:
            print ("Low link quality: %s", quality)

    def _run(self):
        print ("Running...")
        current_time = 0
        self._cf.commander.send_setpoint (0,0,0,0);
        while current_time <= 5:
            print (current_time)
            self._quadcopter._update(self._cf)
            time.sleep(0.1)
            current_time += 0.1
        self._cf.close_link()
        print ("Done.")
        


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print ("Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()
    print ("Crazyflies found:")
    for i in available:
        print (i[0])
        
    print ("For quadcopter #%s, trying to connection to a radio on channel %s" % (QUADCOPTER_NUMBER, channelForGroup[QUADCOPTER_NUMBER]))
    interface = "radio://0/" + str(channelForGroup[QUADCOPTER_NUMBER]) + "/" + str(BANDWIDTH)
    print ("That means interface %s" % (interface))
    le = Controller (interface)
