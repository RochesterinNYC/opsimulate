#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import os

HOME = os.path.expanduser("~")
OPSIMULATE_HOME = os.path.join(HOME, '.opsimulate')

KEYS_DIR_NAME = os.path.join(OPSIMULATE_HOME, 'keys')
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR_NAME, 'opsimulate')
PUBLIC_KEY_FILE = os.path.join(KEYS_DIR_NAME, 'opsimulate.pub')

SAVED_SELECTED_MODULE_PATH = os.path.join(OPSIMULATE_HOME,
                                          'selected_module.txt')
MODULE_START_SCRIPT = 'initiate'
MODULE_CHECK_SCRIPT = 'check'
MODULE_RESOLVE_SCRIPT = 'resolve'
MODULE_METADATA = 'metadata.yml'

SERVICE_ACCOUNT_FILE = os.path.join(OPSIMULATE_HOME, 'service-account.json')

ZONE = 'us-east4-a'
MACHINE_TYPE = 'n1-standard-1'
UBUNTU_VERSION = 'ubuntu-1404-lts'
INSTANCE_NAME = 'opsimulate-gitlab'
VM_USERNAME = 'opsimulate'
