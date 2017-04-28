"""
Creates an image from a given server
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import OpenstackClient

MY_PATH = os.path.abspath(os.path.dirname(__file__))

ARGS = [
    {'name': 'auth_url', 'help': 'Openstack auth url'},
    {'name': 'username', 'help': 'Openstack project username'},
    {'name': 'password', 'help': 'Openstack project password'},
    {'name': 'project_id', 'help': 'Openstack project ID'},
    {'name': 'instance_name', 'required': True, 'help': 'Name of instance from which to make an instance'},
    {'name': 'image_name', 'required': True, 'help': 'Name of image'}
]

def execute(args):
    """ Creates image """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)

    target_server = [server for server in openstack.connection.servers.list()
                     if server.name == args.instance_name]
    
    if not target_server:
        raise Exception("Instance '{}' not found".format(args.instance_name))
    elif len(target_server) > 1:
        raise Exception("Found {} instances of " \
                        "instance '{}'".format(len(target_server),
                                             args.instance_name))
    else:
        target_server[0].create_image(args.image_name)
    
        