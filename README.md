# [opsimulate](https://pypi.python.org/pypi/opsimulate)
Georgia Tech OMSCS EduTech Class Project

## Description

The opsimulate CLI will allow students to start a simulation of a production incident on an actual server that they can then investigate, debug, and fix. The opsimulate CLI will have the functionality to create servers, setup the server packages and configuration in a specific way, setup and run a service, provide the student with SSH access to the server, and setup an incident from an incident module. The opsimulate CLI tool will also provide hints and a description of and also solution for (if asked for) the incident. It can also check whether the student has successfully resolved the incident.

## Motivation

There are currently no free, open-source simulation-based learning frameworks or tools available for gaining sysadmin/devops related technical operational skills, knowledge, and experience. 

## Dependencies

- Python (2 or 3)
- a GCP Account

## Installation

`pip install opsimulate`

## GCP Setup 

- Sign into GCP account using a Google account at console.cloud.google.com (Gmail works)

![GCP Sign In](/docs/screenshots/gcp-sign-in.png?raw=true "GCP Sign In")

- At the [GCP Home Dashboard](https://console.cloud.google.com/projectselector/home/dashboard), create a project.

![GCP Create Project](/docs/screenshots/create-project.png?raw=true "GCP Create Project")

![GCP Naming Project](/docs/screenshots/naming-project.png?raw=true "GCP Naming Project")

- Go the IAM --> Service Accounts page.

![GCP Service Accounts](/docs/screenshots/service-accounts-in-menu.png?raw=true "GCP Service Accounts")

- Create a service account. Make sure you select the option to "Furnish a new private key"
  of the "JSON" Key Type.

![GCP Create Service Account](/docs/screenshots/create-service-account.png?raw=true "GCP Create Service Account")

Also, make sure you give the service account the Project Owner role.

![GCP Project Owner Role](/docs/screenshots/service-account-role.png?raw=true "GCP Project Owner Role")

- Creating the service account will automatically download the service account credentials.

- Set `GOOGLE_APPLICATION_CREDENTIALS` to where the GCP service account credentials are:

  Ex. `export GOOGLE_APPLICATION_CREDENTIALS=~/Downloads/opsimulate-omscs-gatech-64486fd95a36.json`

## Usage

- `opsimulate setup`
- `opsimulate deploy`

- Select a problem module via `opsimulate module_select`
- Start the problem simulation via `opsimulate module_start`
- Run `opsimulate connect` and run resulting SSH command to connect to server
- Try to fix
- If you need help/hints, run `opsimulate module_hint`
- Run `opsimulate module_check` to check if the problem has been fixed
- If you can't fix the issue yourself, run `opsimulate module_resolve` to end the problem simulation
- Run `opsimulate clean` to clean up local artifacts (ex. generated SSH keys) and tear down GCP resources like the VM

## Commands

- `opsimulate status` = Check the status of GCP credentials and selected problem module
- `opsimulate setup` = Setup the ~/.opsimulate artifacts directory
- `opsimulate deploy` = Deploy the GCP VM with Gitlab and setup SSH access
- `opsimulate connect` = Print the SSH command that can be used to get onto the Gitlab VM
- `opsimulate clean` = Clean up the GCP Gitlab VM and generated SSH keys
- `opsimulate module_select` = Select a problem module
- `opsimulate module_start` = Start the problem simulation
- `opsimulate module_hint` = Get a hint about the problem
- `opsimulate module_check` = Check if the problem has been resolved
- `opsimulate module_resolve` = Resolve the problem

## Docker Workflow

```
docker build -t opsimulate .
docker run -v <absolute path to service account json>:/root/.opsimulate/service-account.json -v <absolute path to module>:/tmp/module -it opsimulate bash
```

## Pypi Build/Upload Workflow

```
python setup.py sdist
python setup.py sdist upload -r pypitest
python setup.py sdist upload -r pypi
```
