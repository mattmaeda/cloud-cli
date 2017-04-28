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
    {'name': 'image_name', 'required': True, 'help': 'Name of image to delete'}
]

def execute(args):
    """ Creates image """
    openstack = OpenstackClient(auth_url=args.auth_url,
                                username=args.username,
                                password=args.password,
                                project_id=args.project_id)
    
    image = openstack.connection.images.find(name=args.image_name)
    image.delete()