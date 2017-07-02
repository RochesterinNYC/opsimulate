#!/bin/bash -e

DEBIAN_FRONTEND=noninteractive apt-get install -y postfix

# System and network debugging tools
sudo apt-get install -y git htop sysstat traceroute

# Gitlab dependencies
sudo apt-get install -y curl openssh-server ca-certificates

# Gitlab installation
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo apt-get install gitlab-ce

sudo gitlab-ctl reconfigure
