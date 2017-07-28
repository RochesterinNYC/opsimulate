#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import json
import os
import random
import shutil
import subprocess
import yaml

from apiclient import discovery
import googleapiclient

import opsimulate.constants as constants
import opsimulate.exceptions as exceptions


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
        },
        'tags': {
            'items': [constants.GITLAB_TAG]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=constants.ZONE,
        body=config).execute()


def enable_network_access_gitlab():
    print("Adding HTTP access to Gitlab instance")

    compute = get_gce_client()
    project = get_service_account_info().get('project_id')
    body = {
        'description': 'HTTP access to Gitlab instances',
        'targetTags': [constants.GITLAB_TAG],
        'allowed': [
          {
            'IPProtocol': 'tcp',
            'ports': ['80']
          },
        ],
        'name': constants.HTTP_ACCESS_FIREWALL_RULE
    }
    compute.firewalls().insert(
        project=project,
        body=body
    ).execute()
    print("Added HTTP access to Gitlab instance")


def create_opsimulate_home_dir():
    # Ensure OPSIMULATE home directory exists
    if not os.path.isdir(constants.OPSIMULATE_HOME):
        print("Generating opsimulate home directory at {}"
              .format(constants.OPSIMULATE_HOME))
        os.mkdir(constants.OPSIMULATE_HOME)


def delete_opsimulate_home_dir():
    # Clean local machine of generated artifacts
    if os.path.isdir(constants.OPSIMULATE_HOME):
        print('Removing {} directory'.format(constants.OPSIMULATE_HOME))
        shutil.rmtree(constants.OPSIMULATE_HOME)


def delete_gce_vm():
    print("Attempting to tear down Gitlab VM")

    compute = get_gce_client()
    project = get_service_account_info().get('project_id')

    try:
        compute.instances().delete(
            project=project,
            zone=constants.ZONE,
            instance=constants.INSTANCE_NAME).execute()
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 404:
            print("Teardown of Gitlab VM instance '{}' unneeded because VM "
                  "does not exist".format(constants.INSTANCE_NAME))
        else:
            raise(e)
    else:
        print("Tore down Gitlab VM")


def disable_network_access_gitlab():
    print("Attempting to tear down Gitlab HTTP access firewall rule")

    compute = get_gce_client()
    project = get_service_account_info().get('project_id')

    try:
        compute.firewalls().delete(
            project=project,
            firewall=constants.HTTP_ACCESS_FIREWALL_RULE).execute()
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 404:
            print("Disabling Gitlab HTTP access unneeded because "
                  "appropriate firewall rule '{}' does not exist"
                  .format(constants.HTTP_ACCESS_FIREWALL_RULE))
        else:
            raise(e)
    else:
        print("Tore down Gitlab HTTP access firewall rule")


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

        subprocess.call("ssh-keygen -t rsa -f {} -C {} -N ''".format(
                        constants.PRIVATE_KEY_FILE, constants.VM_USERNAME),
                        shell=True)
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


def gitlab_service_ready():
    ip_address = running_vm_ip_address()
    grep_command = "grep '{}' {}".format(
        constants.GITLAB_READY_LOG_MESSAGE, constants.GITLAB_LOG)
    check_gitlab_ready_command = \
        '''ssh -i {} -o "StrictHostKeyChecking no" {}@{} "{}"'''.format(
            constants.PRIVATE_KEY_FILE, constants.VM_USERNAME,
            ip_address, grep_command)

    return (subprocess.call(check_gitlab_ready_command, shell=True,
                            stdout=open(os.devnull, "w"),
                            stderr=subprocess.STDOUT) == 0)


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


# -------------------
# Validation methods
# -------------------


def validate_module_metadata(module_path):
    module_metadata_file = os.path.join(module_path, constants.MODULE_METADATA)

    with open(module_metadata_file, 'r') as f:
        metadata = yaml.load(f)

    module_metadata_correct = True
    incorrect_keys = []
    for key in metadata:
        if key not in constants.ACCEPTED_METADATA_KEYS:
            module_metadata_correct = False
            incorrect_keys.append("'{}'".format(key))
    if not module_metadata_correct:
        error_msg = ('Module metadata includes improper keys: {}'
                     .format(', '.join(incorrect_keys)))
        raise exceptions.ModuleMetadataError(error_msg)


def validate_module_contents(module_path):
    module_contents_correct = True
    missing_files = []
    for required_file in constants.REQUIRED_MODULE_FILES:
        file_path = os.path.join(module_path, required_file)
        if not os.path.isfile(file_path):
            module_contents_correct = False
            missing_files.append("'{}'".format(required_file))

    if not module_contents_correct:
        error_msg = ('Module missing required files: {}'
                     .format(', '.join(missing_files)))
        raise exceptions.ModuleMetadataError(error_msg)


def validate_module_scripts_executable(module_path):
    scripts_executable = True
    non_executable_files = []
    for script in constants.REQUIRED_MODULE_SCRIPTS:
        file_path = os.path.join(module_path, script)
        if not os.access(file_path, os.X_OK):
            scripts_executable = False
            non_executable_files.append("'{}'".format(script))

    if not scripts_executable:
        error_msg = ('Following module scripts need to be executable: {}'
                     .format(', '.join(non_executable_files)))
        raise exceptions.ModuleScriptsExecutableError(error_msg)


def validate_vm_running():
    if not running_vm_instance():
        error_msg = ("The VM instance has not been created yet. "
                     "Run 'opsimulate deploy'")
        raise exceptions.VMNotRunningError(error_msg)


def validate_opsimulate_home_present():
    if not os.path.isdir(constants.OPSIMULATE_HOME):
        error_msg = ("The opsimulate home directory has not been setup yet. "
                     "Run 'opsimulate setup'")
        raise exceptions.HomeDirNotSetupError(error_msg)


def validate_credentials_loaded():
    if not os.path.isfile(constants.SERVICE_ACCOUNT_FILE):
        error_msg = ("The GCP service account credentials json file has not "
                     "been loaded yet. Run 'opsimulate load_credentials "
                     "<credentials_path>'")
        raise exceptions.GCPCredentialsNotLoadedError(error_msg)


def validate_module_selected():
    if not os.path.isfile(constants.SAVED_SELECTED_MODULE_PATH):
        error_msg = ("No module has been selected yet. "
                     "Run 'opsimulate module_select <module_path>'")
        raise exceptions.ModuleNotSelectedError(error_msg)
