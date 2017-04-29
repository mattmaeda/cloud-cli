"""
Finds a volume and attaches it to an instance
"""
import logging.config
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient
from instance_util import get_instance
from volume_util import get_volume_details, attach_volume_to_instance

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
    {'name': 'instance_name', 'help': 'Name of the server'},
    {'name': 'volume_name', 'help': 'Name of volume'},
    {'name': 'volume_id', 'help': 'ID of the volume'}
]

def execute(args):
    """ Find volume and attach to an instance

        Note that as of the 12.0.0 Liberty release,
        the Nova libvirt driver no longer honors a
        user-supplied device name. This is the same
        behavior as if the device name parameter is
        not supplied on the request.

    """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)


    instance = get_instance_by_name(openstack, args.instance_name)
    volume = get_volume_details(openstack, volume_name=args.volume_name,
                                volume_id=args.volume_id)

    attach_volume_to_instance(openstack, instance, volume)


def get_instance_by_name(client, instance_name):
    """ Gets instance by instance name """
    instance = get_instance(client, instance_name)

    if instance is None:
        logging.error("Unable to load instance " \
                      "'{}'".format(instance_name))
        sys.exit(1)

    return instance

