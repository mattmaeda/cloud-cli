"""
Connects to Openstack environment and stops an instance
"""
import logging.config
import os
import novaclient
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient
from util import get_instance

MY_PATH = os.path.abspath(os.path.dirname(__file__))
OPENSTACK_DIR = os.path.abspath(os.path.join(MY_PATH, os.pardir))
IMPLEMENTATION_DIR = os.path.abspath(os.path.join(OPENSTACK_DIR, os.pardir))
CLI_BASE_PATH = os.path.abspath(os.path.join(IMPLEMENTATION_DIR, os.pardir))

ALREADY_STOPPED_PATTERN = "Cannot 'stop' instance .* while it is in vm_state stopped"
logging.config.fileConfig(os.path.join(CLI_BASE_PATH, 'logging.conf'))

ARGS = [
    {'name': 'auth_url', 'help': 'Openstack auth url'},
    {'name': 'username', 'help': 'Openstack project username'},
    {'name': 'password', 'help': 'Openstack project password'},
    {'name': 'project_id', 'help': 'Openstack project ID'},
    {
        'name': 'instance_name',
        'required': True,
        'help': 'Name of instance to stop'
    }
]

def execute(args):
    """ Stops a running instance """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)

    instance = get_instance(openstack, args.instance_name)

    if instance is None:
        logging.error("Unable to load instance " \
                      "'{}'".format(args.instance_name))
        sys.exit(1)

    else:
        try:
            instance.stop()
        except novaclient.exceptions.Conflict, conflict_exception:
            pattern = re.compile(ALREADY_STOPPED_PATTERN)
            if pattern.match(conflict_exception.message):
                logging.warning("Instance '{}' " \
                                "already stopped".format(args.instance_name))
            else:
                raise conflict_exception
