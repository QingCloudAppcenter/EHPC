#!/usr/bin/env python

import os.path as os_path
from common import (
    backup,
    run_shell,
    get_cluster_info,
)
from constants import (
    RESOURCE_INFO_FILE,
    BACKUP_SLURM_CONF_CMD,
    APP_HOME,
    SLURM_CONF,
    SLURM_CONF_TMPL,
    COMPUTE_HOSTNAME_PREFIX,
    CONTROLLER_HOSTNAME_PREFIX,
)


def get_ctl_machine():
    cluster_info = get_cluster_info()
    controllers = cluster_info["controllers"]
    controllers.sort(key=lambda x: x[0])
    # eg:
    # SlurmctldHost=controller1(10.0.191.219)
    # SlurmctldHost=controller2(10.0.3.169)
    # 1st one must be controller1
    ctl_machine = "SlurmctldHost={}{}({})".format(
        CONTROLLER_HOSTNAME_PREFIX, controllers[0][0], controllers[0][1])
    for controller in controllers:
        if controller[0] > 1:
            ctl_machine = "{}\nSlurmctldHost={}{}({})".format(ctl_machine,
                CONTROLLER_HOSTNAME_PREFIX, controller[0], controller[1])
    return ctl_machine


def generate_conf():
    # get cluster_name
    cluster_info = get_cluster_info()
    cls_name = cluster_info["cluster_name"]

    ctl_resource = ""  # the first line in resource.info
    cmp_resource = ""  # the last line in resource.info
    with open(RESOURCE_INFO_FILE, "r") as info:
        lines = info.readlines()
        for line in lines:
            if line:
                if not ctl_resource:
                    ctl_resource = line
                else:
                    cmp_resource = line

    # generate default NodeName, eg: node[1-6,8,12-15]
    sids = [int(s) for s in cluster_info["sids"].split(",") if s]
    sids.sort()

    node_name = "{}[".format(COMPUTE_HOSTNAME_PREFIX)  # eg: [1-6,8]
    start_sid = sids[0]  # eg: 1
    last_sid = start_sid
    for sid in sids:
        if sid - last_sid > 1:
            if last_sid == start_sid:
                node_name = "{}{},".format(node_name, start_sid)  # eg: [1-6,8,
            else:
                node_name = "{}{}-{},".format(node_name, start_sid, last_sid)  # eg: [1-6,8,12-15]
            start_sid = sid
        last_sid = sid

    if last_sid == start_sid:  # the end of sids
        node_name = "{}{}]".format(node_name, start_sid)
    else:
        node_name = "{}{}-{}]".format(node_name, start_sid, last_sid)

    ctl_machine = get_ctl_machine()

    # backup last slurm configuration
    if os_path.exists(SLURM_CONF):
        backup(BACKUP_SLURM_CONF_CMD)

    # replace slurm.conf.template
    tmp_file = "{}/slurm.conf.tmp".format(APP_HOME)
    with open(tmp_file, "w") as conf:
        with open(SLURM_CONF_TMPL, "r") as tmpl:
            for line in tmpl.readlines():
                if line:
                    line = line.format(CLUSTER_NAME=cls_name,
                                       CONTROL_MACHINE=ctl_machine,
                                       CONTROLLER_RESOURCE=ctl_resource,
                                       COMPUTE_RESOURCE=cmp_resource,
                                       DEFAULT_NODE_NAME=node_name)
                conf.write(line)

    run_shell("mv {} {}".format(tmp_file, SLURM_CONF))
