# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen


class OpsimulateError(Exception):
    """General Opsimulate Error"""


class ModuleValidationError(OpsimulateError):
    """Error with module contents"""


class ModuleMetadataError(ModuleValidationError):
    """Error with format of module metadata"""
