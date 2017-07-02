#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

KEYS_DIR_NAME = './keys'
PRIVATE_KEY_FILE = '{}/opsimulate'.format(KEYS_DIR_NAME)
PUBLIC_KEY_FILE = '{}/opsimulate.pub'.format(KEYS_DIR_NAME)

SERVICE_ACCOUNT_FILE = 'service-account.json'

ZONE = 'us-east4-a'
MACHINE_TYPE = 'n1-standard-1'
UBUNTU_VERSION = 'ubuntu-1404-lts'
INSTANCE_NAME = 'opsimulate-gitlab'
VM_USERNAME = 'opsimulate'
