#!/usr/bin/env python

from common import run_shell, backup
from constants import (
    HOSTS,
    WORK_DIR,
    BACKUP_HOSTS_CMD,
    EHPC_HOSTS_INFO,
)


def generate():
    backup(BACKUP_HOSTS_CMD)

    ori_hosts = []
    with open(HOSTS, "r") as old:
        line = old.readline()
        while line:
            ori_hosts.append(line)
            if "metadata" in line:
                break
            line = old.readline()

    TMP_HOSTS = "{}/hosts".format(WORK_DIR)
    with open(TMP_HOSTS, "w") as hosts:
        for line in ori_hosts:
            hosts.write(line)
        with open(EHPC_HOSTS_INFO, "r") as ehpc_hosts:
            hosts.writelines(ehpc_hosts.readlines())

    run_shell("mv {} {}".format(TMP_HOSTS, HOSTS))
