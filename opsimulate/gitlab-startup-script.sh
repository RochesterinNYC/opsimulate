#!/bin/bash -e

DEBIAN_FRONTEND=noninteractive apt-get install -y postfix

sudo apt-get install -y curl openssh-server ca-certificates

curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo apt-get install gitlab-ce

sudo gitlab-ctl reconfigure
