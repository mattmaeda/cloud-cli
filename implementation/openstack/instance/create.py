"""
Connects to Openstack environment and creates an instance
"""
import os
import sys
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient

MY_PATH = os.path.abspath(os.path.dirname(__file__))

ARGS = [
    {'name': 'auth_url', 'help': 'Openstack auth url'},
    {'name': 'username', 'help': 'Openstack project username'},
    {'name': 'password', 'help': 'Openstack project password'},
    {'name': 'project_id', 'help': 'Openstack project ID'},
    {'name': 'config_file', 'required': True, 'help': 'Path to instance config file'}
]

def execute(args):
    """ Creates instance """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)

    config = None
    with open(args.config_file, "r") as config_file:
        config = yaml.load(config_file)

    server_name = config.get("name")
    image = openstack.connection.images.find(name=config.get("image"))
    flavor = openstack.connection.flavors.find(name=config.get("flavor"))

    network_interfaces = []
    for network_interface in config.get("nics"):
        nic = openstack.connection.networks.find(label=network_interface)
        network_interfaces.append({"net-id": nic.id})
    
    config["nics"] = network_interfaces

    del config["name"]
    del config["image"]
    del config["flavor"]

    openstack.connection.servers.create(server_name, image, flavor, **config)
    openstack.connection.servers.list()

def validate_config_file(config):
    pass