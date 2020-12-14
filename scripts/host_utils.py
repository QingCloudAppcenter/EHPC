#!/usr/bin/env python

from common import run_shell, backup, get_hostname, get_nas_mount_point
from constants import (
    HOSTS,
    APP_HOME,
    BACKUP_HOSTS_CMD,
    HOSTS_INFO_FILE,
    HPC_MODULE_FILES_TMPL,
    HPC_DEFAULT_MODULE_FILE,
    HPC_MODULE_FILES,
    COMPUTE_HOSTNAME_PREFIX,
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

    tmp_hosts = "{}/hosts".format(APP_HOME)
    with open(tmp_hosts, "w") as hosts:
        for line in ori_hosts:
            hosts.write(line)
        with open(HOSTS_INFO_FILE, "r") as ehpc_hosts:
            hosts_lines = ehpc_hosts.readlines()
        for i in range(len(hosts_lines)):
            # replace node1 to node001
            if hosts_lines[i].find(COMPUTE_HOSTNAME_PREFIX) != -1:
                node = hosts_lines[i].split()[1]
                sid = int(node.split(COMPUTE_HOSTNAME_PREFIX)[1])
                new_node = "%s%03d" % (COMPUTE_HOSTNAME_PREFIX, sid)
                hosts_lines[i] = hosts_lines[i].replace(node, new_node)

        hosts.writelines(hosts_lines)

    run_shell("mv {} {}".format(tmp_hosts, HOSTS))


def set_hostname():
    hostname = get_hostname()
    run_shell("hostnamectl set-hostname {}".format(hostname))


def generate_hpcmodulefiles():
    # prepare path for ehpc cluster modulefiles
    nas_mount_point = get_nas_mount_point()
    run_shell("mkdir -p {}/opt/modulefiles/".format(nas_mount_point))
    dft_modulefiles_path = "{}/opt/modulefiles/default".format(nas_mount_point)
    run_shell("cp {} {}".format(HPC_DEFAULT_MODULE_FILE, dft_modulefiles_path))

    # replace slurm.conf.template
    tmp_file = "{}/hpcmodulefiles.tmp".format(APP_HOME)
    with open(tmp_file, "w") as conf:
        with open(HPC_MODULE_FILES_TMPL, "r") as tmpl:
            for line in tmpl.readlines():
                if line and line.find("NAS_MOUNT_POINT") != -1:
                    line = line.format(NAS_MOUNT_POINT=nas_mount_point)
                conf.write(line)

    run_shell("mv {} {}".format(tmp_file, HPC_MODULE_FILES))
