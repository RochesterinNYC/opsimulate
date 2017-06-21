#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 James Wen

import click

@click.group()
def cli():
    print("CLI")
