# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen


class OpsimulateError(Exception):
    """General Opsimulate Error"""


class ModuleValidationError(OpsimulateError):
    """Error with module contents"""


class ModuleMetadataError(ModuleValidationError):
    """Error with format of module metadata"""


class ModuleScriptsExecutableError(ModuleValidationError):
    """Error with module scripts being executable"""


class VMNotRunningError(OpsimulateError):
    """Error with Gitlab VM not running yet"""


class HomeDirNotSetupError(OpsimulateError):
    """Error with Opsimulate home dir not setup yet"""


class ModuleNotSelectedError(OpsimulateError):
    """Error with a module not being selected yet"""
