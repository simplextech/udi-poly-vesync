#!/usr/bin/env python

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import sys
from pyvesync import VeSync
from nodes import vesync_bulb, VeSyncBulbNode

LOGGER = polyinterface.LOGGER


class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'VeSync Controller'
        self.poly.onConfig(self.process_config)
        self.email = None
        self.password = None
        self.default_email = "YourEmail@Domain.com"
        self.default_password = "YourPassword"
        self.vesync = None

    def start(self):
        LOGGER.info('Started VeSync NodeServer')
        self.removeNoticesAll()
        if self.check_params():
            self.removeNoticesAll()
            self.vesync = VeSync(self.email, self.password)
            self.vesync.login()
            self.vesync.update()
            # self.vesync.update_energy()
            self.discover()

    def shortPoll(self):
        # LOGGER.info('Short Poll: Updating Device Information')
        if self.email == self.default_email or self.password == self.default_password:
            LOGGER.info('Please set proper email and password in configuration page, and restart this nodeserver')
        else:
            self.vesync.update()
            # self.vesync.update_energy()

            if len(self.vesync.bulbs) > 0:
                for bulb in self.vesync.bulbs:
                    uuid = bulb.uuid
                    address = uuid.split('-')[-1]
                    status = bulb.connection_status
                    is_on = bulb.is_on
                    level = bulb.brightness

                    for node in self.nodes:
                        if self.nodes[node].address == address:
                            if status == 'online':
                                self.nodes[node].setDriver('GV0', 1)
                            else:
                                self.nodes[node].setDriver('GV0', 0)
                            if is_on:
                                self.nodes[node].setDriver('GV1', 100)
                            else:
                                self.nodes[node].setDriver('GV1', 0)
                            # Set Level
                            self.nodes[node].setDriver('ST', level)

    def longPoll(self):
        pass

    def query(self, command = None):
        # self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        self.vesync.get_devices()

        if len(self.vesync.bulbs) > 0:
            for bulb in self.vesync.bulbs:
                name = bulb.device_name
                uuid = bulb.uuid
                address = uuid.split('-')[-1]
                self.addNode(VeSyncBulbNode(self, self.address, address, 'VeSync - ' + name, bulb))

    def delete(self):
        LOGGER.info('Removing VeSync Nodeserver')

    def stop(self):
        LOGGER.debug('VeSync NodeServer stopped.')
        self.removeNoticesAll()

    def process_config(self, config):
        pass
        # this seems to get called twice for every change, why?
        # What does config represent?
        # LOGGER.info("process_config: Enter config={}".format(config));
        # LOGGER.info("process_config: Exit");

    def check_params(self):
        if 'email' in self.polyConfig['customParams']:
            self.email = self.polyConfig['customParams']['email']
        else:
            self.email = self.default_email
            LOGGER.error('check_params: e-mail not defined in customParams, please add it.  Using {}'.format(self.email))

        if 'password' in self.polyConfig['customParams']:
            self.password = self.polyConfig['customParams']['password']
        else:
            self.password = self.default_password
            LOGGER.error('check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))

        self.addCustomParam({'password': self.password, 'email': self.email})

        if self.email == self.default_email or self.password == self.default_password:
            self.addNotice('Please set proper email and password in configuration page, and restart this nodeserver')
            return False

        self.removeNoticesAll()
        return True

    def remove_notice_test(self, command):
        LOGGER.info('remove_notice_test: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNotice('test')

    def remove_notices_all(self, command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]


if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Template')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
