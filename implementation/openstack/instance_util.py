"""
Utility for Openstack instance commands
"""
import logging.config
import os

MY_PATH = os.path.abspath(os.path.dirname(__file__))
IMPLEMENTATION_DIR = os.path.abspath(os.path.join(MY_PATH, os.pardir))
CLI_BASE_PATH = os.path.abspath(os.path.join(IMPLEMENTATION_DIR, os.pardir))

logging.config.fileConfig(os.path.join(CLI_BASE_PATH, 'logging.conf'))

def get_instance(cloud_cli_openstack_client, server_name):
    """ Gets the instance that matches the given name.
        Returns None in the following conditions:

        1. Not found
        2. More than one instance returned
    """
    all_servers = cloud_cli_openstack_client.connection.servers.list()
    target_server = [server for server in all_servers if server.name == server_name]

    if not target_server:
        logging.warning("Instance '{}' not found".format(server_name))
        return None
    elif len(target_server) > 1:
        logging.warning("Found {} instances of " \
                        "instance '{}'".format(len(target_server), server_name))
        return None
    else:
        return target_server[0]


def get_all_instances(cloud_cli_openstack_client, server_name):
    """ Returns all instances that match the given name
    """
    all_servers = cloud_cli_openstack_client.connection.servers.list()
    target_servers = [server for server in all_servers if server.name == server_name]

    if not target_servers:
        logging.warning("Instance '{}' not found".format(server_name))
        return None
    else:
        return target_servers
