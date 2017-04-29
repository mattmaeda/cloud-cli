"""
Connects to Openstack environment and deletes an instance
"""
import logging.config
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient
from instance_util import get_all_instances

MY_PATH = os.path.abspath(os.path.dirname(__file__))
OPENSTACK_DIR = os.path.abspath(os.path.join(MY_PATH, os.pardir))
IMPLEMENTATION_DIR = os.path.abspath(os.path.join(OPENSTACK_DIR, os.pardir))
CLI_BASE_PATH = os.path.abspath(os.path.join(IMPLEMENTATION_DIR, os.pardir))

logging.config.fileConfig(os.path.join(CLI_BASE_PATH, 'logging.conf'))

ARGS = [
    {'name': 'auth_url', 'help': 'Openstack auth url'},
    {'name': 'username', 'help': 'Openstack project username'},
    {'name': 'password', 'help': 'Openstack project password'},
    {'name': 'project_id', 'help': 'Openstack project ID'},
    {
        'name': 'instance_name',
        'required': True,
        'help': 'Name of instance to delete'
    }
]

def execute(args):
    """ Deletes an instance """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)

    instances = get_all_instances(openstack, args.instance_name)
    delete(instances, args.instance_name)


def delete(instances, instance_name):
    """ Given a list of instances, deletes the specified
        instance if it is in the list
    """
    if instances is None:
        logging.warning("Unable to find instance " \
                      "'{}'".format(instance_name))
    elif len(instances) > 1:
        logging.error("Found {} instances " \
                      "of instance '{}'".format(len(instances),
                                                instance_name))
        sys.exit(1)
    else:
        instance = instances[0]
        instance.delete()
