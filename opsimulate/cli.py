#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import json
import os
from subprocess import call

import click


@click.group()
def cli():
    print("CLI")


@cli.command('deploy')
def deploy():
    # Set max charge/budget constrictions on student’s GCP account
    # Use GCE API client and Gitlab debian package to deploy and setup
    _add_service_account_ssh_key()
    # Setup the student’s investigative tools on the server: ensure common
    # operational tools like curl, iostat, lsop, lsof, w, dig, nslookup, mtr,
    # etc. are present
    # Setup student interface to server by setting up SSH + keys
    # Generate and print an SSH command that they can run in a separate command
    # line/terminal window to initiate an SSH connection with the server
    pass


def _add_service_account_ssh_key():
    service_account_file = 'service-account.json'
    if os.path.isfile(service_account_file):
        print("Adding SSH key to project now")
        with open(service_account_file) as f:
            data = json.load(f)
        key_file = 'service-account-ssh-key'
        with open(key_file, 'w') as f:
            f.write(data['private_key'])
        os.chmod(key_file, 0600)
        call('ssh-add {}'.format(key_file), shell=True)
        os.remove(key_file)
    else:
        print("Your GCP project's owner service account's credentials must be "
              "in the '{}' file.".format(service_account_file))
        exit(1)
