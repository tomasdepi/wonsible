from fabric import Connection
from modules import MODULE_DICT
import yaml
import argparse

parser = argparse.ArgumentParser(description='Parse Playbook and SSH parameters')
parser.add_argument('--playbook_file', '-p', type=str, help='Playbook to execute', dest='playbook_file')
parser.add_argument('--password', '-pw', type=str, help='Password to ssh in', dest='ssh_password')

def main():
    args = parser.parse_args()
    with open(args.playbook_file, 'r') as file:
        data = yaml.safe_load(file)

    host = data.get('host')
    user = data.get('username')

    c = Connection(host=f"{user}@{host}",
                   connect_kwargs={"password": f'{args.ssh_password}'}
                   )

    tasks = data.get('tasks')

    for t in tasks:
        module = t.get('module')
        args = t.get('args')
        MODULE_DICT[module](c, args).run()

if __name__ == '__main__':
    main()
