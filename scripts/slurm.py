#!/usr/bin/env python

from common import backup, run_shell
from constants import (
    CLS_NAME_INFO,
    RESOURCE_INFO,
    CMP_SID_INFO,
    BACKUP_SLURM_CONF_CMD,
    WORK_DIR,
    SLURM_CONF,
    SLURM_CONF_TMPL,
)


def generate_conf():
    # get cluster_name
    with open(CLS_NAME_INFO, "r") as info:
        cls_name = info.read()

    ctl_resource = ""  # the first line in resource.info
    cmp_resource = ""  # the last line in resource.info
    with open(RESOURCE_INFO, "r") as info:
        lines = info.readlines()
        for line in lines:
            if line:
                if not ctl_resource:
                    ctl_resource = line
                else:
                    cmp_resource = line

    # generate default NodeName, eg: node[1-6,8,12-15]
    sids = []
    with open(CMP_SID_INFO, "r") as info:
        for line in info.readlines():
            if line:
                sids.append(int(line))
    sids.sort()

    node_name = "node["  # eg: [1-6,8]
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

    # backup last slurm configuration
    backup(BACKUP_SLURM_CONF_CMD)

    # replace slurm.conf.template
    TMP = "{}/slurm.conf.tmp".format(WORK_DIR)
    with open(TMP, "w") as conf:
        with open(SLURM_CONF_TMPL, "r") as tmpl:
            for line in tmpl.readlines():
                if line:
                    line = line.format(CLUSTER_NAME=cls_name,
                                       CONTROLLER_RESOURCE=ctl_resource,
                                       COMPUTE_RESOURCE=cmp_resource,
                                       DEFAULT_NODE_NAME=node_name)
                conf.write(line)

    run_shell("mv {} {}".format(TMP, SLURM_CONF))
