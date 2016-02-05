# CrazyfliePLS
Pioneer Library System's Python wrapper for the Crazyflie 2.0

## Installation

To use this setup for a class, first install Python 2.7 in its default install
location (C:\Python27). Then run the PythonUSB.bat batch script provided to install
the necessary Python library to talk to the CrazyRadioPA. Download the Python controller
code from the Crazyflie site and copy its lib folder to the same location as the 
CrazyfliePLS.py.

## Use

1. Open the CrazyfliePLS.py file using IDLE (you will probably have to right-click on the file). 
2. Locate the large red comment block near the top that says "CRITICAL" in it and update the quadcopter number to match the kit you are using.
3. Locate the green arrow that points to the *first* _update function in the file. All changes should be made within that function.

Students' task is to modify the code in the _update function to make their quadcopter accomplish whatever the day's objective is (e.g. "take off at one pad and lad at another" etc.). Several functions are provided:

```
increaseAltitude(x) # Go upwards at x meters per second (approximately)
holdAltitude()      # Hold the current height
decreaseAltitude(x) # Go down at x meters per second (approximately)
setPitch(x)         # Pitch foward (positive x) or backward (negative x) degrees
setRoll(x)          # Roll right (positive x) or left (negative x) degrees
setYawRate(x)       # Rotate around the center of the quadcopter at x degrees per second (approximately)
shutdown(cf)        # Shut everything off and disconnect
```

An example run might look like:
```
if self._time < 1.0:
  self.increaseAltitude(1) # Go up at 1 meter per second
elif self._time < 2.0:
  self.holdAltitude() # Hold the current altitude
elif self._time < 4.0:
  self.decreaseAltitude(0.5) # Land at about 1/2 meter per second
else:
  self.shutdown(cf) # Shut down
  return
```
This simple run goes up to about one meter in the first second, hovers at about 1 meter off the 
ground for one second, then slowly lands over the course of the next two seconds.

A more complicated example:
```
if self._time < 1.0:
  self.increaseAltitude(1) # Go up at 1 meter per second
elif self._time < 3.0:
  self.holdAltitude() # Hold the current altitude
  self.setPitch (20) # Pitch forward at 20 degrees to accelerate forward
elif self._time < 4.0:
  self.setPitch (-20) # Pitch backward to decelerate
elif self._time < 6.0:
  self.setPitch (0) # Level off
  self.decreaseAltitude(0.5) # Land at about 1/2 meter per second
else:
  self.shutdown(cf) # Shut down
  return
```
This takes off to about a meter in height, then accelerates forward for two seconds. It then slows back down to approximately a stop over the next second (you will have to play with the time and the angle of pitch to get a perfect stop). FInally, it levels off and lands.
