from fabric import Connection
from modules import MODULE_DICT
from constants import PLAYBOOK_MANDATORY_KEYS
from utils import parse_yaml_file, get_missing_mandatory_keys
import argparse

parser = argparse.ArgumentParser(description='Parse Playbook and SSH parameters')
parser.add_argument('-f', '--playbook_file', type=str, help='Playbook to execute', dest='playbook_file', required=True)
parser.add_argument('-u', '--username', type=str, help='Username to ssh in', dest='ssh_user', required=True)
parser.add_argument('-p', '--password', type=str, help='Password to ssh in', dest='ssh_password', required=True)

def main():
    args = parser.parse_args()

    parsed_playbook = parse_yaml_file(args.playbook_file)

    missing_args = get_missing_mandatory_keys(PLAYBOOK_MANDATORY_KEYS, parsed_playbook)

    if missing_args:
        print(f'Can not parse the playbook, there are missing arguments, aborting')
        print(missing_args)
        exit(1)

    host = parsed_playbook.get('host')
    user = args.ssh_user

    c = Connection(host=f"{user}@{host}",
                   connect_kwargs={"password": f'{args.ssh_password}'}
                   )

    tasks = parsed_playbook.get('tasks')

    for t in tasks:
        module = t.get('module')
        args = t.get('args')
        MODULE_DICT[module](c, args).run()

if __name__ == '__main__':
    main()
