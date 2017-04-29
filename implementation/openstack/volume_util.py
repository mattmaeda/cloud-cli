"""
Helper functions for volume actions for Openstack

Warning

These APIs are proxy calls to the Volume service. Nova has deprecated all
the proxy APIs and users should use the native APIs instead. These will
fail with a 404 starting from microversion 2.36.

See: Relevant Volume APIs.
http://developer.openstack.org/api-ref-blockstorage-v2.html#volumes-v2-volumes

Note:
Once the Openstack SDK is updated to support volume actions, change
these URL requests to leverage the library
"""
import logging.config
import os
import re
import novaclient

METHOD_GET = "GET"
METHOD_POST = "POST"

URL_VOLUME = "/os-volumes"
URL_ATTACH_VOLUME = "/servers/%(instance_id)s/os-volume_attachments"


MY_PATH = os.path.abspath(os.path.dirname(__file__))
IMPLEMENTATION_DIR = os.path.abspath(os.path.join(MY_PATH, os.pardir))
CLI_BASE_PATH = os.path.abspath(os.path.join(IMPLEMENTATION_DIR, os.pardir))

ALREADY_IN_USE_PATTERN = "Invalid volume: volume '.*' status must be 'available'. Currently in 'in-use'"

logging.config.fileConfig(os.path.join(CLI_BASE_PATH, 'logging.conf'))


def make_volume_url_request(os_client, url, method, body=None):
    """ Volume URL request wrapper """
    logging.info("Making request to '{}'".format(url))

    if body is not None:
        (response, body) = os_client.connection.client.request(url,
                                                               method,
                                                               body=body)
    else:
        (response, body) = os_client.connection.client.request(url, method)

    if response.status_code != 200:
        msg = "Volume Creation Error Reason: {}".format(response.reason)
        raise Exception(msg)

    return body


def get_volume_details(openstack_client, volume_name=None, volume_id=None):
    """ Takes openstack client and either volume name or volume ID
        and returns the status of the volume
    """
    if volume_name is None and volume_id is None:
        raise AssertionError("Either volume name or volume ID must be defined")

    body = make_volume_url_request(openstack_client, URL_VOLUME, METHOD_GET)

    total_matches = 0
    volume_information = {}

    for details in body.get("volumes"):
        volume_instance_name = details.get("displayName")
        volume_instance_id = details.get("id")

        if volume_id is not None and volume_instance_id == volume_id:
            return details

        elif(volume_name is not None
             and volume_instance_name is not None
             and volume_name == volume_instance_name):

            volume_information = details
            total_matches += 1

        else:
            continue

    if total_matches > 1:
        raise Exception("Found {} instances of " \
                        "volume name {}".format(total_matches, volume_name))

    return volume_information



def create_volume_helper(openstack_client, user_entered_cli_args=None,
                         volume_configuration=None):
    """ Takes openstack client and either user entered cli args or
        volume configuration dictionary.BaseException

        Returns the volume ID if successful
    """
    volume = {}

    if user_entered_cli_args is not None:
        volume["size"] = user_entered_cli_args.size

        if user_entered_cli_args.availability_zone:
            volume["availability_zone"] = user_entered_cli_args.availability_zone
        if user_entered_cli_args.display_name:
            volume["display_name"] = user_entered_cli_args.display_name
        if user_entered_cli_args.snapshot_id:
            volume["snapshot_id"] = user_entered_cli_args.snapshot_id

    elif volume_configuration is not None:
        volume = volume_configuration

    else:
        raise AssertionError("No volume configuration defined")

    request_body = {"volume": volume}

    body = make_volume_url_request(openstack_client, URL_VOLUME, METHOD_POST,
                                   body=request_body)

    return body.get("volume").get("id")


def attach_volume_to_instance(openstack_client, instance, volume):
    """ Attaches a volume to an instance

        Note that as of the 12.0.0 Liberty release, the Nova libvirt
        driver no longer honors a user-supplied device name. This is
        the same behavior as if the device name parameter is not supplied
        on the request.
    """
    url = URL_ATTACH_VOLUME % {"instance_id": instance.id}

    request_body = {"volumeAttachment": {"volumeId": volume.get("id")}}

    try:
        body = make_volume_url_request(openstack_client, url, METHOD_POST,
                                       body=request_body)

    except novaclient.exceptions.BadRequest, bad_request:
        pattern = re.compile(ALREADY_IN_USE_PATTERN)

        if pattern.match(bad_request.message):
            logging.warning("Volume '{}' already " \
                            "in use".format(volume.get("id")))

        else:
            raise bad_request
