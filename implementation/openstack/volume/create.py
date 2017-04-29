"""
Creates an volume
"""
import logging.config
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient
from volume_util import create_volume_helper

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
    {'name': 'size', 'required': True, 'help': 'Size of the volume'},
    {'name': 'availability_zone', 'help': 'Availabillty Zone for the volume'},
    {'name': 'display_name', 'help': 'Display name of the volume'},
    {'name': 'snapshot_id', 'help': 'Snapshot ID from which to create the volume'}
]

def execute(args):
    """ Creates volume """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)

    volume_id = create_volume_helper(openstack, user_entered_cli_args=args)
    logging.info("Volume ID '{}' is being created".format(volume_id))


