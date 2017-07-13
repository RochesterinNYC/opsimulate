#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import json
import os
import random
import shutil
from subprocess import call
import yaml

from apiclient import discovery
import googleapiclient
import click

import opsimulate.constants as constants


@click.group()
def cli():
    print("CLI")


@cli.command('setup')
def setup():
    # Ensure OPSIMULATE home directory exists
    if not os.path.isdir(constants.OPSIMULATE_HOME):
        print("Generating opsimulate home directory at {}"
              .format(constants.OPSIMULATE_HOME))
        os.mkdir(constants.OPSIMULATE_HOME)


@cli.command('clean')
def clean():
    # Clean local machine of generated artifacts
    if os.path.isdir(constants.KEYS_DIR_NAME):
        print("Removing 'keys' directory")
        shutil.rmtree(constants.KEYS_DIR_NAME)

    # Destroy created Gitlab VM
    print("Attempting to tear down Gitlab VM")
    compute = _get_gce_client()
    project = _get_service_account_info().get('project_id')

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


@cli.command('connect')
def connect():
    vm_instance_info = _running_vm_instance()
    if vm_instance_info:
        ip_address = vm_instance_info.get('networkInterfaces')[0] \
            .get('accessConfigs')[0].get('natIP')

        ssh_command = "ssh -i {} -o 'StrictHostKeyChecking no' {}@{}".format(
            constants.PRIVATE_KEY_FILE, constants.VM_USERNAME, ip_address)
        print("To connect to your running VM instance, execute the "
              "following command:")
        print(ssh_command)
    else:
        print("The VM instance has not been created yet. "
              "Run 'opsimulate deploy'")


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


@cli.command('module_select')
@click.argument('module_path', type=click.Path(exists=True))
def module_select(module_path):
    if os.path.isabs(module_path):
        abs_module_path = module_path
    else:
        current_dir = os.getcwd()
        abs_module_path = os.path.join(current_dir, module_path)

    with open(constants.SAVED_SELECTED_MODULE_PATH, 'w') as f:
        f.write(abs_module_path)
    print('Saved path of selected module to {}'.format(
        constants.SAVED_SELECTED_MODULE_PATH))


@cli.command('module_start')
def module_start():
    print("Initiating module problem")

    vm_instance_info = _running_vm_instance()

    ip_address = vm_instance_info.get('networkInterfaces')[0] \
        .get('accessConfigs')[0].get('natIP')

    if os.path.isfile(constants.SAVED_SELECTED_MODULE_PATH):
        with open(constants.SAVED_SELECTED_MODULE_PATH, 'r') as f:
            selected_module_path = f.read().strip()

    module_start_script = os.path.join(selected_module_path,
                                       constants.MODULE_START_SCRIPT)

    module_start_command = \
        "ssh -i {} -o 'StrictHostKeyChecking no' {}@{} 'bash -s' < {}".format(
            constants.PRIVATE_KEY_FILE, constants.VM_USERNAME, ip_address,
            module_start_script)

    if call(module_start_command, shell=True) == 0:
        print("Initiated module problem")
    else:
        print("Initiating module problem failed")


@cli.command('module_hint')
def module_hint():
    print("Here's a hint:")

    if os.path.isfile(constants.SAVED_SELECTED_MODULE_PATH):
        with open(constants.SAVED_SELECTED_MODULE_PATH, 'r') as f:
            selected_module_path = f.read().strip()

    module_metadata_file = os.path.join(
        selected_module_path, constants.MODULE_METADATA)

    with open(module_metadata_file, 'r') as f:
        module_metadata = yaml.load(f)

    hints = module_metadata.get('hints')
    hint = random.choice(hints)
    print(hint)


@cli.command('module_check')
def module_check():
    print('Checking if module problem has been fixed...')

    vm_instance_info = _running_vm_instance()

    ip_address = vm_instance_info.get('networkInterfaces')[0] \
        .get('accessConfigs')[0].get('natIP')

    if os.path.isfile(constants.SAVED_SELECTED_MODULE_PATH):
        with open(constants.SAVED_SELECTED_MODULE_PATH, 'r') as f:
            selected_module_path = f.read().strip()

    module_check_script = os.path.join(selected_module_path,
                                       constants.MODULE_CHECK_SCRIPT)

    module_check_command = \
        "ssh -i {} -o 'StrictHostKeyChecking no' {}@{} 'bash -s' < {}".format(
            constants.PRIVATE_KEY_FILE, constants.VM_USERNAME, ip_address,
            module_check_script)

    if call(module_check_command, shell=True) == 0:
        print("Module problem has been fixed. Great job!")
    else:
        print("Module problem is still an issue. Keep trying, you got this!")


@cli.command('status')
def status():
    print('Opsimulate Status')
    if os.path.isfile(constants.SAVED_SELECTED_MODULE_PATH):
        with open(constants.SAVED_SELECTED_MODULE_PATH, 'r') as f:
            selected_module_path = f.read().strip()
        if not selected_module_path:
            selected_module_path_message = 'No module selected'
        else:
            selected_module_path_message = selected_module_path
    else:
        selected_module_path_message = 'No module selected'
    print('Selected Module: {}'.format(selected_module_path_message))

    if os.path.isfile(constants.SERVICE_ACCOUNT_FILE):
        service_account_credentials_message = constants.SERVICE_ACCOUNT_FILE
    else:
        service_account_credentials_message = \
            'No GCP service account credentials present'
    print('GCP SA Credentials: {}'.format(service_account_credentials_message))


def _create_gce_vm():
    print("Creating GCE VM")

    zone_machine_type = 'zones/{}/machineTypes/{}'.format(
        constants.ZONE, constants.MACHINE_TYPE)

    compute = _get_gce_client()
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family=constants.UBUNTU_VERSION).execute()
    source_disk_image = image_response['selfLink']

    project = _get_service_account_info().get('project_id')
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


def _enable_network_access_gitlab():
    compute = _get_gce_client()
    project = _get_service_account_info().get('project_id')

    print("Adding HTTP and HTTPS access to Gitlab instance")

    instance_info = _running_vm_instance()
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


def _get_gce_client():
    return discovery.build('compute', 'v1')


def _get_service_account_info():
    if os.path.isfile(constants.SERVICE_ACCOUNT_FILE):
        with open(constants.SERVICE_ACCOUNT_FILE) as f:
            data = json.load(f)
        return data
    else:
        print("Your GCP project's owner service account's credentials must be "
              "in the '{}' file.".format(constants.SERVICE_ACCOUNT_FILE))
        exit(1)


def _generate_ssh_key():
    if not os.path.isdir(constants.KEYS_DIR_NAME):
        print("Generating SSH key")
        os.mkdir(constants.KEYS_DIR_NAME)

        call("ssh-keygen -t rsa -f {} -C {} -N ''".format(
            constants.PRIVATE_KEY_FILE, constants.VM_USERNAME), shell=True)
        os.chmod(constants.PRIVATE_KEY_FILE, 0400)
        print('Generated SSH key')


def _running_vm_instance():
    compute = _get_gce_client()
    project = _get_service_account_info().get('project_id')
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
