try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
from pyvesync import VeSync


class VeSyncBulbNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, bulb):
        super(VeSyncBulbNode, self).__init__(controller, primary, address, name)
        self.bulb = bulb

    def start(self):
        status = self.bulb.connection_status
        is_on = self.bulb.is_on
        level = self.bulb.brightness
        # print(self.name, status, is_on, level)

        if status == 'online':
            self.setDriver('GV0', 1)
        else:
            self.setDriver('GV0', 0)

        if is_on:
            self.setDriver('GV1', 100)
        else:
            self.setDriver('GV1', 0)

        # Set Level
        self.setDriver('ST', level)

    def setOn(self, command):
        if 'value' in command.keys():
            val = int(command['value'])
            if val == 0:
                # self.bulb.set_brightness(val)
                self.bulb.turn_off()
                self.setDriver('GV1', 0)
                # self.setDriver('OL', val)
            else:
                self.bulb.set_brightness(val)
                self.setDriver('GV1', 100)
                self.setDriver('ST', val)
        else:
            self.bulb.turn_on()
            self.setDriver('GV1', 100)

    def setOff(self, command):
        self.bulb.turn_off()
        self.setDriver('GV1', 0)

    def setLevel(self, command):
        print('setLevel command: ', command)
        val = int(command['value'])
        if val > 0:
            self.bulb.set_brightness(val)
            self.setDriver('GV1', 100)
            self.setDriver('ST', val)
        else:
            self.bulb.set_brightness(val)
            self.setDriver('GV1', 0)
            self.setDriver('ST', val)

    def query(self, command = None):
        self.bulb.update()
        status = self.bulb.connection_status
        is_on = self.bulb.is_on
        level = self.bulb.brightness

        if status == 'online':
            self.setDriver('GV0', 1)
        else:
            self.setDriver('GV0', 0)

        if is_on:
            self.setDriver('GV1', 100)
        else:
            self.setDriver('GV1', 0)

        # Set Level
        self.setDriver('ST', level)
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1,2,3,4]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 51},
        {'driver': 'GV0', 'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 0, 'uom': 78}
    ]

    id = 'vesyncbulb'
    """
    id of the node from the nodedefs.xml that is in the profile.zip. This tells
    the ISY what fields and commands this node has.
    """
    commands = {
                    'QUERY': query, 'DON': setOn, 'DOF': setOff, 'OL': setLevel
                }
    """
    This is a dictionary of commands. If ISY sends a command to the NodeServer,
    this tells it which method to call. DON calls setOn, etc.
    """