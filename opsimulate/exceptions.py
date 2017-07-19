# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen


class OpsimulateError(Exception):
    """General Opsimulate Error"""


class ModuleMetadataError(OpsimulateError):
    """Error with format of module metadata"""
