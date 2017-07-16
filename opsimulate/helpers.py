#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import json
import os
import random
from subprocess import call
import yaml

from apiclient import discovery
import googleapiclient

import opsimulate.constants as constants


def create_gce_vm():
    print("Creating GCE VM")

    zone_machine_type = 'zones/{}/machineTypes/{}'.format(
        constants.ZONE, constants.MACHINE_TYPE)

    compute = get_gce_client()
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family=constants.UBUNTU_VERSION).execute()
    source_disk_image = image_response['selfLink']

    project = get_service_account_info().get('project_id')
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'gitlab-startup-script.sh'), 'r').read()

    with open(constants.PUBLIC_KEY_FILE) as f:
        public_key = f.read()

    config = {
        'name': constants.INSTANCE_NAME,
        'machineType': zone_machine_type,
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
                    "value": '{}:{}\n'.format(constants.VM_USERNAME, public_key)
                }
            ]

        }
    }

    return compute.instances().insert(
        project=project,
        zone=constants.ZONE,
        body=config).execute()


def enable_network_access_gitlab():
    compute = get_gce_client()
    project = get_service_account_info().get('project_id')

    print("Adding HTTP and HTTPS access to Gitlab instance")

    instance_info = running_vm_instance()
    fingerprint = instance_info.get('labelFingerprint')

    body = {
        "items": ['http-server', 'https-server'],
        "fingerprint": fingerprint
    }
    compute.instances().setTags(
        project=project,
        zone=constants.ZONE,
        instance=constants.INSTANCE_NAME,
        body=body
    ).execute()
    print("Added HTTP and HTTPS access to Gitlab instance")


def get_gce_client():
    return discovery.build('compute', 'v1')


def get_service_account_info():
    if os.path.isfile(constants.SERVICE_ACCOUNT_FILE):
        with open(constants.SERVICE_ACCOUNT_FILE) as f:
            data = json.load(f)
        return data
    else:
        print("Your GCP project's owner service account's credentials must be "
              "in the '{}' file.".format(constants.SERVICE_ACCOUNT_FILE))
        exit(1)


def generate_ssh_key():
    if not os.path.isdir(constants.KEYS_DIR_NAME):
        print("Generating SSH key")
        os.mkdir(constants.KEYS_DIR_NAME)

        call("ssh-keygen -t rsa -f {} -C {} -N ''".format(
            constants.PRIVATE_KEY_FILE, constants.VM_USERNAME), shell=True)
        os.chmod(constants.PRIVATE_KEY_FILE, 0400)
        print('Generated SSH key')


def running_vm_instance():
    compute = get_gce_client()
    project = get_service_account_info().get('project_id')
    try:
        return compute.instances().get(
            project=project,
            zone=constants.ZONE,
            instance=constants.INSTANCE_NAME).execute()
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 404:
            return None
        else:
            raise e


def running_vm_ip_address():
    vm_instance_info = running_vm_instance()

    ip_address = vm_instance_info.get('networkInterfaces')[0] \
        .get('accessConfigs')[0].get('natIP')

    return ip_address


def file_from_selected_module(desired_file):
    if os.path.isfile(constants.SAVED_SELECTED_MODULE_PATH):
        with open(constants.SAVED_SELECTED_MODULE_PATH, 'r') as f:
            selected_module_path = f.read().strip()
    return os.path.join(selected_module_path, desired_file)


def selected_module_metadata():
    module_metadata_file = file_from_selected_module(
        constants.MODULE_METADATA)

    with open(module_metadata_file, 'r') as f:
        module_metadata = yaml.load(f)
    return module_metadata


def get_seen_hints():
    if os.path.isfile(constants.HINT_HISTORY_FILE):
        with open(constants.HINT_HISTORY_FILE, 'r') as f:
            seen_hints = yaml.load(f)
    else:
        seen_hints = []
    return seen_hints


def get_new_hint():
    seen_hints = get_seen_hints()

    # Get new hint
    all_hints = selected_module_metadata().get('hints')
    unseen_hints = list(set(all_hints) - set(seen_hints))
    if unseen_hints:
        hint = random.choice(unseen_hints)
        seen_hints.append(hint)
    else:
        hint = 'No new hints available!'

    # Record seen hints
    with open(constants.HINT_HISTORY_FILE, 'w') as f:
        yaml.dump(seen_hints, f, default_flow_style=False)

    return hint


def clear_hint_history():
    if os.path.isfile(constants.HINT_HISTORY_FILE):
        os.remove(constants.HINT_HISTORY_FILE)
