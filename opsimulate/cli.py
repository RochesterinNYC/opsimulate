#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import os
import zipfile

import click
from requests import get


@click.group()
def cli():
    print("CLI")


@cli.command('deploy')
def deploy():
    # Set max charge/budget constrictions on student’s GCP account
    # Use Terraform and Gitlab terraform template to deploy and setup
    _setup_terraform()
    # Setup the student’s investigative tools on the server: ensure common
    # operational tools like curl, iostat, lsop, lsof, w, dig, nslookup, mtr,
    # etc. are present
    # Setup student interface to server by setting up SSH + keys
    # Generate and print an SSH command that they can run in a separate command
    # line/terminal window to initiate an SSH connection with the server
    pass


def _setup_terraform():
    """
    Setup the dependencies necessary to deploy the simulation software
    """
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
