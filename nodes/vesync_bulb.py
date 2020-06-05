try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface


LOGGER = polyinterface.LOGGER


class VeSyncBulbNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, bulb):
        super(VeSyncBulbNode, self).__init__(controller, primary, address, name)
        self.bulb = bulb

    def start(self):
        status = self.bulb.connection_status
        is_on = self.bulb.is_on
        if is_on:
            level = self.bulb.brightness
        else:
            level = 0

        if status == 'online':
            self.setDriver('GV0', 1, force=True)
            if is_on:
                self.setDriver('GV1', 100, force=True)
                self.setDriver('ST', level, force=True)
            else:
                self.setDriver('GV1', 0, force=True)
                self.setDriver('ST', 0, force=True)
        else:
            self.setDriver('GV0', 0, force=True)
            self.setDriver('ST', level, force=True)

    def setOn(self, command):
        level = self.bulb.brightness
        val = int(command['value'])
        if val == 0:
            self.bulb.turn_off()
            self.setDriver('GV1', 0, force=True)
            self.setDriver('ST', 0, force=True)
        elif val > 0:
            self.bulb.set_brightness(val)
            self.setDriver('GV1', 100, force=True)
            self.setDriver('ST', val, force=True)
        else:
            self.bulb.turn_on()
            self.setDriver('GV1', 100, force=True)
            self.setDriver('ST', level, force=True)

    def setOff(self, command):
        self.bulb.turn_off()
        self.setDriver('GV1', 0, force=True)
        self.setDriver('ST', 0, force=True)

    def setLevel(self, command):
        # print('setLevel command: ', command)
        val = int(command['value'])
        if val == 0:
            self.bulb.turn_off()
            self.setDriver('GV1', 0, force=True)
            self.setDriver('ST', 0, force=True)
        elif val > 0:
            self.bulb.set_brightness(val)
            self.setDriver('GV1', 100, force=True)
            self.setDriver('ST', val, force=True)
        else:
            LOGGER.info("Invalid Level Selection")

    def query(self, command=None):
        self.bulb.update()
        status = self.bulb.connection_status
        is_on = self.bulb.is_on
        if is_on:
            level = self.bulb.brightness
        else:
            level = 0

        if status == 'online':
            self.setDriver('GV0', 1, force=True)
            if is_on:
                self.setDriver('GV1', 100, force=True)
                self.setDriver('ST', level, force=True)
            else:
                self.setDriver('GV1', 0, force=True)
                self.setDriver('ST', 0, force=True)
        else:
            self.setDriver('GV0', 0, force=True)
            self.setDriver('ST', level, force=True)

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1,2,3,4]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 51},
        {'driver': 'GV0', 'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 0, 'uom': 78}
    ]

    id = 'vesyncbulb'
    commands = {
                    'QUERY': query, 'DON': setOn, 'DOF': setOff, 'OL': setLevel
                }
