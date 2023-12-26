from fabric import Connection
from abc import ABC
from constants import ABSENT_STATE, PRESENT_STATE, TOUCH_STATE, FILE_STATE, DIRECTORY_STATE
from utils import get_missing_mandatory_keys
import os

class TaskModule(ABC):
    def __init__(self, conn: Connection, args: dict):
        self.conn = conn
        self.args = args
        self._check_required_args()

    def _check_required_args(self) -> bool:
        missing_args = get_missing_mandatory_keys(self.required_args, self.args)
        
        if missing_args:
            print(f'The following args are missing for {self.__class__.__name__} module, aborting')
            print(missing_args)
            exit(1)

class Command(TaskModule):
    def __init__(self, conn: Connection, args: dict):
        self.required_args = ['cmd']
        super().__init__(conn, args)
        self.cmd = args['cmd']

    def run(self):
        print(f'Running command: {self.cmd}')
        self.conn.run(self.cmd)

class Package(TaskModule):
    def __init__(self, conn: Connection, args: dict):
        self.required_args = ['name', 'state']
        super().__init__(conn, args)

        self.package_name = args['name']
        self.state = args['state']
        self.version = args.get('version', None)

    def _is_package_installed(self) -> bool:
        return not bool(self.conn.run(f'dpkg -s {self.package_name}', hide=True, warn=True).return_code)

    def _install_package(self):
        install_command = f'apt install -y {self.package_name}'
        if self.version:
            install_command += f'={self.version}'

        self.conn.sudo(install_command)

    def _uninstall_package(self):
        self.conn.sudo(f'apt remove -y {self.package_name}')
        self.conn.sudo(f'apt auto-remove -y')

    def _get_package_version(self) -> str:
        return self.conn.run(f'dpkg -l | awk \'$2=="{self.package_name}" {{ print $3 }}\'', hide=True, warn=True).stdout.rstrip()

    def run(self):
        if self.state == PRESENT_STATE and self._is_package_installed():
            if self._get_package_version() == self.version:
                print('Nothing to do, package is already installed and same version')
            else:
                print('Package found but other version, trying to update')
                self._install_package()

        elif self.state == ABSENT_STATE and not self._is_package_installed():
            print('Nothing to do, package is not installed')

        elif self.state == PRESENT_STATE and not self._is_package_installed():
            self._install_package()
            print(f'package {self.package_name} installed')

        elif self.state == ABSENT_STATE and self._is_package_installed():
            self._uninstall_package()
            print('package {self.package_name} uninstalled')

class File(TaskModule):
    def __init__(self, conn, args):
        self.required_args = ['path', 'state']
        super().__init__(conn, args)        

        self.path = args['path']
        self.state = args['state']

        self.argument_to_command = {
            'owner': 'chown',
            'group': 'chgrp',
            'mode': 'chmod',
        }

    def _check_resource_exist(self) -> bool:
        return not bool(self.conn.run(f'test -e {self.path}', warn=True).return_code)
    
    def _delete_resource(self):
        if not self._check_resource_exist():
            print('Resource does not exist, aborting....')
            exit(1)

        self.conn.run(f'rm -rf {self.path}')

    def run(self):
        if self.state == TOUCH_STATE:
            if self._check_resource_exist():
                print(f'File {self.path} already exists')
            else:
                self.conn.run(f'touch {self.path}')
        elif self.state == ABSENT_STATE:
            self._delete_resource()
            return
        elif self.state == FILE_STATE:
            base_file = os.path.basename(self.path)
            self.conn.put(self.args['src'], f'/tmp/{base_file}')
            self.conn.sudo(f'mv /tmp/{base_file} {self.path}')
        elif self.state == DIRECTORY_STATE:
            if self._check_resource_exist():
                print(f'Directory {self.path} already exists')
            else:
                self.conn.run(f'mkdir -p {self.path}')
                print(f'Directory {self.path} created')

        for config in self.argument_to_command.keys():
            if config in self.args:
                self.conn.sudo(f'{self.argument_to_command[config]} {self.args[config]} {self.path}')


class Service(TaskModule):
    def __init__(self, conn, args):
        self.required_args = ['name', 'state']
        super().__init__(conn, args)        

        self.service_name = args['name']
        self.state = args['state']

    def run(self):
        self.conn.sudo(f'service {self.service_name} {self.state}')


MODULE_DICT = {
    'command': Command,
    'package': Package,
    'file': File,
    'service': Service,
}
