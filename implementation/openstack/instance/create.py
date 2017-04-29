"""
Connects to Openstack environment and creates an instance
"""
import os
import sys
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient

MY_PATH = os.path.abspath(os.path.dirname(__file__))
SAMPLE_CONFIG_TEMPLATE = os.path.join(MY_PATH, "create-instance.yml.template")
DEFAULT_SETTINGS_FILE = os.path.join(MY_PATH, "default-settings.yml")

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


    config = load_config(openstack, args.config_file)
    create_instance(openstack, config)


def load_config_file(path_to_config):
    """ Loads YAML config file and returns config dictionary """
    if os.path.exists(path_to_config):
        with open(path_to_config) as config_file:
            return yaml.load(config_file)

    else:
        raise Exception("Configuration file '%s' not found" % path_to_config)


def load_config(openstack, path_to_config):
    """ Load the user defined config file, overlays the defaults,
        validates, and translates it before returning it
    """
    config = load_config_file(path_to_config)
    overlay_default_configurations(config)

    if not validate_config_file(config):
        raise Exception("Malformed configuration file.  See %s " \
                        "for required inputs" % SAMPLE_CONFIG_TEMPLATE)

    translate_configuration(openstack, config)

    return config


def overlay_default_configurations(user_defined_config):
    """ Takes the user-define configs and overlays
        default settings, if defined and if the user
        has not already defined the setting
    """
    defaults = {}

    if os.path.exists(DEFAULT_SETTINGS_FILE):
        defaults = load_config_file(DEFAULT_SETTINGS_FILE)

    for param, value in defaults.iteritems():
        if param not in user_defined_config:
            user_defined_config[param] = value
        elif user_defined_config[param] is None:
            user_defined_config[param] = value


def validate_config_file(config_settings):
    """ Confirms that the minimum required values are set
        in the configuration file
    """
    required_values = ["name", "image", "flavor", "security_groups", "nics",
                       "key_name", "availability_zone"]
    valid = [config_settings.get(value) is not None for value in required_values]

    return False not in valid


def translate_configuration(openstack, config):
    """ Takes user-defined settings and translates them to
        Openstack resource values where applicable

        For now, just network interfaces are translated
    """
    translate_network_settings(openstack, config)


def translate_network_settings(openstack, config):
    """ Takes network settings and translates them to
        the appropriate Openstack resource IDs
    """
    network_interfaces = []
    for network_interface in config.get("nics"):
        nic = openstack.connection.networks.find(label=network_interface)
        network_interfaces.append({"net-id": nic.id})

    config["nics"] = network_interfaces


def create_instance(openstack, config):
    """ Takes the validated config and creates the instance(s) """
    server_name = config.get("name")
    image = openstack.connection.images.find(name=config.get("image"))
    flavor = openstack.connection.flavors.find(name=config.get("flavor"))

    del config["name"]
    del config["image"]
    del config["flavor"]

    openstack.connection.servers.create(server_name, image, flavor, **config)
    openstack.connection.servers.list()
