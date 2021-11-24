# [opsimulate](https://pypi.python.org/pypi/opsimulate)
Georgia Tech OMSCS EduTech Class Project

## Description

The opsimulate CLI allows students to deploy a working, accessible Gitlab instance and then start a simulation of a production incident with that Gitlab instance that they can investigate, debug, and fix. The opsimulate CLI will have the functionality to create servers, setup the server packages and configuration in a specific way, setup and run a Gitlab service, provide the student with SSH access to the server, and setup an incident from an incident module. The opsimulate CLI tool will also provide hints and a description of and also solution for (if asked for) the incident. It can also check whether the student has successfully resolved the incident.

## Motivation

There are currently no free, open-source simulation-based learning frameworks or tools available for gaining sysadmin/devops related technical operational skills, knowledge, and experience. 

## Dependencies

- Python 2.x
- a Google Compute Platform Account

## Installation

`pip install opsimulate`

## Google Compute Platform Setup 

- Sign into your GCP account using a Google account at [console.cloud.google.com](console.cloud.google.com) (Gmail works). Please create a Google account if you do not have one.

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

- Creating the service account will automatically download the service account credentials. It will download as a json file. Note where the credentials json file downloaded to because it will be required when you run `opsimulate load_credentials` to properly copy over the GCP credentials.

## Usage/Workflow

Optional: Set the UBUNTU_VERSION environment variable to select the [operating system version](https://cloud.google.com/compute/docs/images/os-details). Defaults to 'ubuntu-1804-lts'. 

- Run `opsimulate setup` to setup the home `~/.opsimulate` directory that opsimulate generates artifacts in.
- Run `opsimulate load_credentials <path to GCP-service-account-credentials.json>` to load in the GCP service account credentials.
- Run `opsimulate deploy` to create the Gitlab instance and make it accessible.
- Run `opsimulate status` until the output displays that both the VM and Gitlab are up and ready.
- Select a problem module via `opsimulate module_select <path to problem module dir>`
- Start the problem simulation via `opsimulate module_start`
- In a separate command line window, run `opsimulate connect` and run the printed SSH command to connect to your Gitlab server.
- Investigate, debug, fix, do whatever you need to figure out what the issue is and how to fix it.
- If you need help/hints, run `opsimulate module_hint` as many times as you need.
- If at any time, you want to check if the problem has been fixed, run `opsimulate module_check`. 
- If you can't fix the issue yourself, run `opsimulate module_resolve` to fix the issue and end the problem simulation. Your Gitlab instance will still be up.
- When you're completely done, run `opsimulate clean` to clean up local artifacts (ex. generated SSH keys) and tear down GCP resources like the Gitlab VM.

## Commands

- `opsimulate status` = Check the status of GCP credentials, selected problem module, VM and Gitlab status
- `opsimulate setup` = Setup the ~/.opsimulate artifacts directory
- `opsimulate load_credentials` = Copy over the GCP service account credentials into ~/.opsimulate directory
- `opsimulate deploy` = Deploy the GCP VM with Gitlab and setup SSH access
- `opsimulate connect` = Print the SSH command that can be used to get onto the Gitlab VM
- `opsimulate clean` = Clean up the GCP Gitlab VM and generated SSH keys
- `opsimulate module_select` = Select a problem module
- `opsimulate module_start` = Start the problem simulation
- `opsimulate module_hint` = Get a hint about the problem
- `opsimulate module_check` = Check if the problem has been resolved
- `opsimulate module_resolve` = Resolve the problem

## Contributing

See the [CONTRIBUTING.md](./CONTRIBUTING.md)


## Docker Workflow

Running/testing opsimulate source:

```
docker build -t opsimulate-testing -f Dockerfile.testing .
docker run -v <absolute path to service account json>:/root/.opsimulate/service-account.json -v <absolute path to module>:/tmp/module -it opsimulate-testing bash
```

Running opsimulate (from Pypi) in a container:

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
