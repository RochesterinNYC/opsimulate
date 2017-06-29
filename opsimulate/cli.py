#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import json
import os
from subprocess import call

from apiclient import discovery
import click


@click.group()
def cli():
    print("CLI")


@cli.command('deploy')
def deploy():
    # Set max charge/budget constrictions on student’s GCP account
    # Use GCE API client and Gitlab debian package to deploy and setup
    # Setup student interface to server by setting up SSH + keys
    _generate_ssh_key()
    _create_gce_vm()
    _enable_network_access_gitlab()
    # Setup the student’s investigative tools on the server: ensure common
    # operational tools like curl, iostat, lsop, lsof, w, dig, nslookup, mtr,
    # etc. are present
    # Generate and print an SSH command that they can run in a separate command
    # line/terminal window to initiate an SSH connection with the server


def _create_gce_vm():
    print("Creating GCE VM")

    NAME = 'opsimulate-gitlab'
    ZONE = 'us-east4-a'
    MACHINE_TYPE = "zones/%s/machineTypes/n1-standard-1" % ZONE
    UBUNTU_VERSION = 'ubuntu-1404-lts'

    compute = _get_gce_client()
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family=UBUNTU_VERSION).execute()
    source_disk_image = image_response['selfLink']

    project = _get_service_account_info().get('project_id')
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'gitlab-startup-script.sh'), 'r').read()

    PUBLIC_KEY_FILE = './keys/opsimulate.pub'
    USERNAME = 'opsimulate'

    with open(PUBLIC_KEY_FILE) as f:
        public_key = f.read()

    config = {
        'name': NAME,
        'machineType': MACHINE_TYPE,
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image
                }
            }
        ],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        'metadata': {
            'items': [
                {
                    'key': 'startup-script',
                    'value': startup_script
                },
                {
                    "key": "ssh-keys",
                    "value": '{}:{}\n'.format(USERNAME, public_key)
                }
            ]

        }
    }

    return compute.instances().insert(
        project=project,
        zone=ZONE,
        body=config).execute()


def _enable_network_access_gitlab():
    print("Adding HTTP and HTTPS access to Gitlab instance")

    NAME = 'opsimulate-gitlab'
    compute = _get_gce_client()
    ZONE = 'us-east4-a'
    project = _get_service_account_info().get('project_id')

    instance_info = compute.instances().get(
        project=project,
        zone=ZONE,
        instance=NAME
    ).execute()
    fingerprint = instance_info.get('labelFingerprint')

    body = {
        "items": ['http-server', 'https-server'],
        "fingerprint": fingerprint
    }
    compute.instances().setTags(
        project=project,
        zone=ZONE,
        instance=NAME,
        body=body
    ).execute()
    print("Added HTTP and HTTPS access to Gitlab instance")


def _get_gce_client():
    return discovery.build('compute', 'v1')


def _get_service_account_info():
    service_account_file = 'service-account.json'
    if os.path.isfile(service_account_file):
        with open(service_account_file) as f:
            data = json.load(f)
        return data
    else:
        print("Your GCP project's owner service account's credentials must be "
              "in the '{}' file.".format(service_account_file))
        exit(1)


def _generate_ssh_key():
    DIR_NAME = "./keys"
    if not os.path.isdir(DIR_NAME):
        print("Generating SSH key")
        os.mkdir(DIR_NAME)
        PRIVATE_KEY_FILE = './keys/opsimulate'
        USERNAME = 'opsimulate'

        call("ssh-keygen -t rsa -f {} -C {} -N ''".format(PRIVATE_KEY_FILE, USERNAME), shell=True)
        os.chmod(PRIVATE_KEY_FILE, 0400)
        print('Generated SSH key')
