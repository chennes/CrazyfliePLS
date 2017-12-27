"""
HOW TO USE THIS FILE:

This file is for Quadcopter instructor use: it's designed to analyze
the quality of the reception in the room and recommend which quadcopters
to use based on where the "clean" frequencies are.

"""



# Don't change this unless you reset the firmware on the quadcopters too
BANDWIDTH = "2M" # others are "250K" and "1M"


# Leave these "import" lines alone, you need them
import sys
import re
import time
import operator
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
    manually programmed each quadcopter to use these channels.

    NOTE: Channel 0 is unused: for clarity, quadcopter 1 is on channel 5 and it
    counts up from there, so channel = quadcopterNumber*5

    """
channelForGroup = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]














class Controller:
    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
        self._cf.link_quality_updated.add_callback(self._quality_updated)

        self._cf.open_link(link_uri)
        self.quality = -1
        self.failed = False

    def linkQuality(self):
        return self.quality

    def connectionFailed(self):
        return self.failed

    def closeLink(self):
        self._cf.close_link()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._cf.close_link()

    def __del__(self):
        self._cf.close_link()

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        self.failed = False

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        self.failed = True

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        self.failed = True

    def _quality_updated(self, quality):
        if quality < self.quality or self.quality == -1:
            self.quality = quality


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print ("Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()
    print ("Crazyflies found:")
    regex = "radio://0/(\d{1,2})/(.+)"
    matcher = re.compile(regex)
    crazyflieConnections = dict()
    for i in available:
        matches = matcher.match(i[0])
        try:
            channel = int(matches.group(1))
            quadcopterNumber = int(channel / 5)
            bandwidth = matches.group(2)
            if not bandwidth == BANDWIDTH:
                continue
            print ("Quadcopter %s on channel %s with bandwidth %s" % (quadcopterNumber, channel, bandwidth))
            try:
                qc = Controller(i[0])
                counter = 0
                while counter < 10 and not qc.connectionFailed():
                    time.sleep(1)
                    counter += 1
                if qc.connectionFailed():
                    crazyflieConnections[quadcopterNumber] = 0
                else:
                    crazyflieConnections[quadcopterNumber] = int(qc.linkQuality())
                qc.closeLink()
            except:
                e = sys.exc_info()[0]
                print (e)
                crazyflieConnections[quadcopterNumber] = 0
        except:
            print ("Could not covert %s to an integer" %(matches.group(1)))

    sortedByStrength = sorted(crazyflieConnections.items(), key=operator.itemgetter(1))
    print ("\n\nSIGNAL STRENGTH RESULTS")
    print ("-----------------------")
    for qc in reversed(sortedByStrength):
        print ("Quadcopter %s: %s%%" % (qc[0], qc[1]), end="")
        if qc[1] < 50:
            print (" (Poor connection!) ")
        else:
            print (" (OK)")
        
