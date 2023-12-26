# Wonsible

An Ansible implementation for Wonolo

## Disclaimer

For the Ubuntu 18.04 environment, I reused a Dockerfile of my own authory that I used back in the days I was learning Ansible, that file (along others) and some playbooks, can be found [in this repo](https://github.com/tomasdepi/ansible)

## Playbook Structure

| Parameter | Comments                                                                                                                               |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------|
| host      | IP or hostname of the remote endpoint                                                                                                  |
| username  | SSH username                                                                                                                           |
| tasks     | List of tasks, each task must have 'module' and 'args' attributes Refer to each Module documentation for required additional arguments |

## Modules

As requested, this tool supports multiple modules and functionalities listed bellow:

* package (install/remove a package)
* file (create/upload/delete remote file)
* service (start/stop/restart)
* update (package manager)
* directory (create/delete)
* command (run random remote commands)


I decided to merge some into the same module, since the purposes are related (like create a file and directory), therefore we have four modules but they support the six fuctionalities

### Package Module

It serves to manage packages, install, remove or upgrade to specific versions

| Argument  | Required | Comments                                                             |
|-----------|----------|----------------------------------------------------------------------|
| name      |   True   | Package name                                                         |
| state     |   True   | Wheter the package is installed or not (present orabsent)            |
| version   |   False  | Version of the package, if not defined, default version will be used |

### File Module

Useful for creating and removing files or directories, additonally it serves to set owner, group and permissions

| Argument | Required | Comments                                                                        |
|----------|----------|---------------------------------------------------------------------------------|
| state    |  True    | if absent deletes the resource, if touch creates an empty file, if directory creates a new directory, if file copies a file to local to remote server |
| path     |  True    | Path of the directory or file                                                   |
| owner    |  False   | Specify an owner                                                                |
| group    |  False   | Specify a group                                                                 |
| mode     |  False   | Specify permissions for read, write and execute                                 |
| src      |  False   | if state is file, path to the source file in the local machine to copy          |

### Service Module

Controls the services on the remote machine, the support options are
* start
* stop
* restart

| Argument  | Required | Comments                          |
|-----------|----------|-----------------------------------|
| name      |   True   | Package name                      |
| state     |   True   | start, stop or restart            |

### Command Module

This Module invokes arbitratry commands

| Argument | Required | Comments                     |
|----------|----------|------------------------------|
|cmd       |  True    | Arbitrary cli command to run | 
