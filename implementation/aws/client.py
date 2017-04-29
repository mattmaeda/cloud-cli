"""
AWS Client
"""
import logging.config
import json
import os
import boto.cloudformation
import boto.ec2
import boto.iam
import boto.s3
import boto.vpc


MY_PATH = os.path.abspath(os.path.dirname(__file__))
IMPLEMENTATION_DIR = os.path.abspath(os.path.join(MY_PATH, os.pardir))
CLI_BASE_PATH = os.path.abspath(os.path.join(IMPLEMENTATION_DIR, os.pardir))

AWS_CONFIG_FILE = os.path.join(MY_PATH, "config.json")
logging.config.fileConfig(os.path.join(CLI_BASE_PATH, 'logging.conf'))


class AWSClient(object):
    """ Contains the boto client object and facilitates the various
        connection methods to Openstack
    """
    def __init__(self, aws_region=None, aws_access_key_id=None,
                 aws_secret_access_key=None):
        config = None
        with open(AWS_CONFIG_FILE) as config_file:
            config = json.load(config_file)

        if aws_region is not None:
            config["region"] = aws_region
        if aws_access_key_id is not None:
            config["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key is not None:
            config["aws_secret_access_key"] = aws_secret_access_key

        region = config["region"]
        del config["region"]

        self.iam_connection = boto.iam.connect_to_region(region, **config)
        self.cloudformation_connection = boto.cloudformation.connect_to_region(
            region, **config
        )
        self.vpc_connection = boto.vpc.connect_to_region(region, **config)
        self.ec2_connection = boto.ec2.connect_to_region(region, **config)
        self.s3_connection = boto.s3.connect_to_region(region, **config)
