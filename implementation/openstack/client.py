"""
Openstack Client
"""
import logging.config
import json
import os
from keystoneauth1 import session
from keystoneauth1 import identity
from novaclient import client


MY_PATH = os.path.abspath(os.path.dirname(__file__))
IMPLEMENTATION_DIR = os.path.abspath(os.path.join(MY_PATH, os.pardir))
CLI_BASE_PATH = os.path.abspath(os.path.join(IMPLEMENTATION_DIR, os.pardir))

OPENSTACK_CONFIG_FILE = os.path.join(MY_PATH, "config.json")
logging.config.fileConfig(os.path.join(CLI_BASE_PATH, 'logging.conf'))


class OpenstackClient(object):
    """ Contains the novaclient client object and facilitates
        the various connection methods to Openstack
    """
    def __init__(self, auth_url=None, username=None, password=None,
                 project_id=None):
        config = None
        with open(OPENSTACK_CONFIG_FILE) as config_file:
            config = json.load(config_file)

        if auth_url is not None:
            config["auth_url"] = auth_url
        if username is not None:
            config["username"] = username
        if password is not None:
            config["password"] = password
        if project_id is not None:
            config["project_id"] = project_id

        auth = identity.Password(**config)
        sess = session.Session(auth=auth)
        self.connection = client.Client(2, session=sess)
