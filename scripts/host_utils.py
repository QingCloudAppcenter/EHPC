#!/usr/bin/env python

from common import run_shell, backup, get_hostname
from constants import (
    HOSTS,
    WORK_DIR,
    BACKUP_HOSTS_CMD,
    HOSTS_INFO,
)


def generate_hosts():
    backup(BACKUP_HOSTS_CMD)

    ori_hosts = []
    with open(HOSTS, "r") as old:
        line = old.readline()
        while line:
            ori_hosts.append(line)
            if "metadata" in line:
                break
            line = old.readline()

    tmp_hosts = "{}/hosts".format(WORK_DIR)
    with open(tmp_hosts, "w") as hosts:
        for line in ori_hosts:
            hosts.write(line)
        with open(HOSTS_INFO, "r") as ehpc_hosts:
            hosts.writelines(ehpc_hosts.readlines())

    run_shell("mv {} {}".format(tmp_hosts, HOSTS))


def set_hostname():
    hostname = get_hostname()
    run_shell("hostnamectl set-hostname {}".format(hostname))
