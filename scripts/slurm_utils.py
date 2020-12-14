#!/usr/bin/env python

import os
import StringIO
import os.path as os_path
from common import (
    logger,
    backup,
    write_file,
    run_shell,
    exec_shell,
    get_cluster_info,
    get_last_cmpnode_list,
    convert_nodes_to_nodeid_list,
    update_queues_node_from_nodeid,
    get_slurm_nodelist_from_sids,
    get_current_cmpnode_list,
)
from constants import (
    RESOURCE_INFO_FILE,
    BACKUP_SLURM_CONF_CMD,
    APP_HOME,
    SLURM_CONF,
    SLURM_CONF_TMPL,
    COMPUTE_HOSTNAME_PREFIX,
    CONTROLLER_HOSTNAME_PREFIX,
    NODE_RESOURCE_FMT,
    DEFAULT,
    NODES,
    PARTITION_NAME,
    MIN_MODES,
    ALLOW_ACCOUNTS,
    EXCLUSIVE_USER,
    STATE,
    PARTITION_CONTROLLER,
    ACTION_GET_TIMEOUT,
    NODEID_LIST,
    PARTITION_CONF_FMT,
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


def get_slurm_cmpnode_list(cluster_info):
    # generate default NodeName, eg: node[1-6,8,12-15]
    sids = [int(s) for s in cluster_info["sids"].split(",") if s]
    sids.sort()
    nodelist = get_slurm_nodelist_from_sids(sids)
    return nodelist


def generate_slurm_conf():
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

    node_list = get_slurm_cmpnode_list(cluster_info)
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
                                       DEFAULT_NODE_NAME=node_list)
                conf.write(line)

    run_shell("mv {} {}".format(tmp_file, SLURM_CONF))


def update_cmpnodes_res_conf(filename):
    """
    update compute node resource in slurm configuration
    :param filename:
    :return:
    """
    # read slurm.conf
    if not os.path.isfile(filename):
        logger.error("%s is not exists", filename)
        return -1

    cluster_info = get_cluster_info()
    # 1. get compute node resource
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

    # get modified compute node
    node_list = get_slurm_cmpnode_list(cluster_info)

    buf = StringIO.StringIO()
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("NodeName=node"):
                # put Slurm Partition conf here
                line = NODE_RESOURCE_FMT.format(node_list, cmp_resource)

            buf.write("\n")
            buf.write(line)

    content = buf.getvalue()
    buf.close()

    write_file(filename, content)
    return 0


def get_queues_details():
    queues_info = {}
    code, out, err = exec_shell("scontrol show partitions",
                                timeout=ACTION_GET_TIMEOUT)
    if code == 0:
        logger.info("get queue details out sting[%s]", out)

        partitions = out.split("\n\n")
        for partition in partitions:
            if partition != "":
                queue = {}
                for i in partition.split():
                    ele = i.split("=")
                    queue.update({ele[0]: ele[1]})
                if queue[PARTITION_NAME] != PARTITION_CONTROLLER:
                    nodeid_list = convert_nodes_to_nodeid_list(queue[NODES])
                else:
                    nodeid_list = []
                queue.update({NODEID_LIST: nodeid_list})
                queues_info.update({queue[PARTITION_NAME]: queue})

        # partitions = out.split("\n\n")
        # for partition in partitions:
        #     if partition != "":
        #         # queue_eles = line.split()
        #         queue_eles = [i.split("=")[1] for i in line.split()]
        #
        #
        #         nodeid_list = convert_nodes_to_nodeid_list(queue_eles[9])
        #         queue_name = queue_eles[0].rstrip("*")
        #         default = queue_eles[0].endwith("*")
        #         if queue_eles[0] != "controller":
        #             queues_info.update({
        #                 queue_name: {
        #                     "queue_name": queue_name,
        #                     "default": default,
        #                     "avail": queue_eles[1],
        #                     "timelimit": queue_eles[2],
        #                     "job_size": queue_eles[3],
        #                     "root": queue_eles[4],
        #                     "oversubs": queue_eles[5],
        #                     "groups": queue_eles[6],
        #                     "nodes": queue_eles[7],
        #                     "state": queue_eles[8],
        #                     "nodelist": queue_eles[9],
        #                     "nodeid_list": nodeid_list,
        #                 }
        #             })

    return queues_info


def update_queues_info_with_nodes_change(queues_info):
    # get addition, deletion node_id, then update queues_info
    #   remove deleted node_id from queues_info
    #   add new node_id to default queues_info
    last_cmpnode_list = get_last_cmpnode_list()
    current_sid = get_current_cmpnode_list()
    for node in last_cmpnode_list:
        if node not in list(current_sid):
            node_in_queue = False
            for _, queue in queues_info.iteritems():
                if node in list(queue[NODEID_LIST]):
                    # remove node from queue nodeid_list
                    logger.warn("remove [%s%s] from queue [%s]",
                                COMPUTE_HOSTNAME_PREFIX, node,
                                queue[PARTITION_NAME])
                    queues_info[NODEID_LIST].remove(node)
                    node_in_queue = True
            if not node_in_queue:
                logger.warn("%s%s doesn't belong to any queue",
                            COMPUTE_HOSTNAME_PREFIX, node)
        else:
            current_sid.remove(node)
    # add new node to default queue
    for node in current_sid:
        for _, queue in queues_info.iteritems():
            if queue[DEFAULT]:
                queue[NODEID_LIST].append(node)

    # update queue Nodes for each Partition in queues_info
    update_queues_node_from_nodeid(queues_info)


def get_partition_conf_from_queues(queues_info):
    partitions_conf = "# Partitions\n"
    for _, queue in queues_info.iteritems():
        partition = PARTITION_CONF_FMT.format(queue[PARTITION_NAME],
                                              queue[DEFAULT],
                                              queue[MIN_MODES],
                                              queue[ALLOW_ACCOUNTS],
                                              queue[EXCLUSIVE_USER],
                                              queue[STATE],
                                              queue[NODEID_LIST])
        partitions_conf = partitions_conf + partition + "\n"
    return partitions_conf


def update_queues_conf_file(filename, queues_info):
    # read specific slurm.conf
    if not os.path.isfile(filename):
        logger.error("%s is not exists", filename)
        return -1

    partitions_conf = get_partition_conf_from_queues(queues_info)
    logger.info("partition conf will be %s", partitions_conf)
    partition_begin = False
    buf = StringIO.StringIO()
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("PartitionName=controller ") and \
                    partition_begin is False:
                partition_begin = True
                buf.write(line)
            elif partition_begin:
                if not line.startswith("PartitionName="):
                    partition_begin = False
                    # put Slurm Partition conf here
                    buf.write(partitions_conf)
                    buf.write("\n")
                else:
                    # skip current Partition conf
                    logger.info("current partition conf %s is skipped", line)
            else:
                buf.write(line)

    content = buf.getvalue()
    buf.close()

    write_file(filename, content)
    return 0


def update_queues_conf(queues_info):
    # backup last slurm configuration
    if os_path.exists(SLURM_CONF):
        backup(BACKUP_SLURM_CONF_CMD)

    # replace slurm.conf.template
    tmp_file = "{}/slurm.conf.tmp".format(APP_HOME)
    run_shell("cp -f {} {}".format(SLURM_CONF, tmp_file))

    update_queues_conf_file(tmp_file, queues_info)
    run_shell("mv {} {}".format(tmp_file, SLURM_CONF))
    return 0


def update_slurm_conf(update_cmpnode_res=False, nodes_change=False):
    # backup last slurm configuration
    if os_path.exists(SLURM_CONF):
        backup(BACKUP_SLURM_CONF_CMD)

    # replace slurm.conf.template
    tmp_file = "{}/slurm.conf.tmp".format(APP_HOME)
    run_shell("cp -f {} {}".format(SLURM_CONF, tmp_file))

    # update NodeName
    if update_cmpnode_res:
        update_cmpnodes_res_conf(tmp_file)

    # get current queues info
    queues_info = get_queues_details()

    # update queues_info according to nodes changing
    if nodes_change:
        update_queues_info_with_nodes_change(queues_info)

    # update queues_info to slurm conf Partition
    update_queues_conf_file(tmp_file, queues_info)

    run_shell("mv {} {}".format(tmp_file, SLURM_CONF))
    pass
