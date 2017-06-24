#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

from Crypto.PublicKey import RSA
import json
import os
from subprocess import call
import zipfile

import click
import git
from requests import get


@click.group()
def cli():
    print("CLI")


@cli.command('deploy')
def deploy():
    # Set max charge/budget constrictions on student’s GCP account
    # Use Terraform and Gitlab terraform template to deploy and setup
    _generate_ssh_key()
    _add_ssh_key_for_terraform()
    _setup_terraform()
    _get_gitlab_terraform()
    # _run_terraform()
    # Setup the student’s investigative tools on the server: ensure common
    # operational tools like curl, iostat, lsop, lsof, w, dig, nslookup, mtr,
    # etc. are present
    # Setup student interface to server by setting up SSH + keys
    # Generate and print an SSH command that they can run in a separate command
    # line/terminal window to initiate an SSH connection with the server
    pass


def _generate_ssh_key():
    DIR_NAME = "./keys"
    if not os.path.isdir(DIR_NAME):
        print("Generating SSH key")
        os.mkdir(DIR_NAME)

        key = RSA.generate(2048)
        with open("./keys/private.key", 'w') as content_file:
            os.chmod("./keys/private.key", 0600)
            content_file.write(key.exportKey('PEM'))
        pubkey = key.publickey()
        with open("./keys/public.key", 'w') as content_file:
            content_file.write(pubkey.exportKey('OpenSSH'))
        print("Generated SSH key")


def _add_ssh_key_for_terraform():
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


def _setup_terraform():
    """
    Setup the dependencies necessary to deploy the simulation software
    """
    if not os.path.isfile('terraform'):
        # Download terraform zip
        print("Downloading Terraform now...")
        terraform_download_link = 'https://releases.hashicorp.com/terraform/' \
                                  '0.9.10/terraform_0.9.10_darwin_amd64.zip'
        terraform_zip_file = 'terraform.zip'
        with open(terraform_zip_file, "wb") as file:
            response = get(terraform_download_link)
            file.write(response.content)

        # unzip
        zip_ref = zipfile.ZipFile(terraform_zip_file, 'r')
        zip_ref.extractall('.')
        zip_ref.close()
        # terraform binary is available
        print("Terraform is ready")

        os.remove(terraform_zip_file)


def _get_gitlab_terraform():
    DIR_NAME = "/tmp/gitlab-terraform"
    if not os.path.isdir(DIR_NAME):
        print("Fetching gitlab GCE terraform repo")
        REMOTE_URL = "https://gitlab.com/gitlab-terraform/gce.git"
        os.mkdir(DIR_NAME)
        repo = git.Repo.init(DIR_NAME)
        origin = repo.create_remote('origin', REMOTE_URL)
        origin.fetch()
        origin.pull(origin.refs[0].remote_head)
        print("Fetched gitlab GCE terraform repo")
