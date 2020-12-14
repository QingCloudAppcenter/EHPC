#!/usr/bin/env python

import sys
import simplejson as jsmod
import traceback

from common import (
    logger,
    get_cluster_info,
    get_role,
    ArgsParser,
    json_loads,
)
from constants import (
    ACTION_QUEUE_ADD,
    ACTION_QUEUE_GET,
    ACTION_QUEUE_DELETE,
    ACTION_QUEUE_MODIFY,

    ROLE_CONTROLLER,
    MASTER_CONTROLLER_SID,
)
from slurm_utils import (
    get_queues_details,
    update_queues_conf,
)


# queue_list format:
#   [{
#     "queue_name": xxx,     queue name
#   }]
def get(queue_list, ignore_exist=False):
    logger.info("Do get queue[%s] info..", queue_list)

    try:
        queues_info = get_queues_details()
        if queue_list:
            # get specific queue
            for queue in queue_list:
                # queue exist
                if not queues_info.get(queue["name"]):
                    logger.error("The queue[%s] doesn't exist!", queue["name"])
                    if not ignore_exist:
                        return 55
                else:
                    queue.update(queues_info.get(queue["name"]))
        else:
            # get all queues
            queue_list = queues_info

        logger.info("get queue detail: [%s]!", queue_list)
        res = {
            "labels": ["queues"],
            "data": [jsmod.dumps(queue_list, encoding='utf-8')]
        }
        logger.debug("Cluster queues: %s", res)
        print jsmod.dumps(res, encoding='utf-8')
        return 0
    except Exception:
        logger.error("Failed to get queue [%s]: \n%s",
                     queue_list, traceback.format_exc())
        return 1


# queue_list format:
#   [{
#     "queue_name": xxx,     queue name
#     "default": YES/NO,
#     "minnode": 1,
#     "nodelist": xxx,
#     "allowaccounts": xxx,
#     "denyaccounts": xxx,
#     "state": "UP",
#     "max_time": "INFINITE",
#   }]
def add(queue_list, ignore_exist=False):
    logger.info("add slurm queue[%s]..", queue_list)

    try:
        queues_info = get_queues_details()
        if not queue_list:
            # get specific queue
            for queue in queue_list:
                queues_info[queue["name"]].update(queue)
        update_queues_conf(queues_info)
        logger.info("get queue detail: [%s]!", queue_list)
        return 0
    except Exception:
        logger.error("Failed to get queue [%s]: \n%s",
                     queue_list, traceback.format_exc())
        return 1


# queue_list format:
#   [{
#     "queue_name": xxx,     queue name
#   }]
def delete(queue_list, ignore_exist=False):
    logger.info("Do delete queue[%s] info..", queue_list)

    try:
        queues_info = get_queues_details()
        if not queue_list:
            # get specific queue
            for queue in queue_list:
                # queue exist
                if not queues_info.get(queue["name"]):
                    logger.error("The queue[%s] doesn't exist!", queue["name"])
                    if not ignore_exist:
                        return 55
                else:
                    del queues_info[queue["name"]]

        update_queues_conf(queues_info)

        logger.info("the queue detail: [%s] after delete [%s]!",
                    queues_info, queue_list)
        return 1
    except Exception:
        logger.error("Failed to get queue [%s]: \n%s",
                     queue_list, traceback.format_exc())
        return 0


# queue_list format:
#   [{
#     "queue_name": xxx,     queue name
#     "default": YES/NO,
#     "minnode": 1,
#     "nodelist": xxx,
#     "allowaccounts": xxx,
#     "denyaccounts": xxx,
#     "state": "UP",
#     "max_time": "INFINITE",
#   }]
def modify(queue_list, ignore_exist=False):
    logger.info("Do modify queue[%s] info..", queue_list)

    try:
        queues_info = get_queues_details()
        # queue exist
        for queue in queue_list:
            if not queues_info.get(queue["name"]):
                logger.error("The queue[%s] doesn't exist!", queue["name"])
                if not ignore_exist:
                    return 55
            else:
                queues_info[queue["name"]].update(queue)

        update_queues_conf(queues_info)

        logger.info("the queue detail: [%s] after modify [%s]!",
                    queues_info, queue_list)
        return 0
    except Exception:
        logger.error("Failed to get queue [%s]: \n%s",
                     queue_list, traceback.format_exc())
        return 1



def help():
    print "queuectl add/get/delete/passwd/add_admin"


ACTION_MAP = {
    "help": help,
    "--help": help,
    ACTION_QUEUE_GET: get,
    ACTION_QUEUE_ADD: add,
    ACTION_QUEUE_MODIFY: modify,
    ACTION_QUEUE_DELETE: delete,
}


def main(argv):
    role = get_role()
    # 只在一个master controller节点执行此命令
    cluster_info = get_cluster_info()
    if role != ROLE_CONTROLLER or \
            int(cluster_info["sid"]) != MASTER_CONTROLLER_SID:
        logger.info("queue action[%s] not handler on non-master [%s|%s].",
                    argv, role, cluster_info["sid"])
        return
    parser = ArgsParser()
    ret = parser.parse(argv)
    if not ret:
        sys.exit(40)

    if parser.action in ACTION_MAP:
        if parser.directive:
            queue = parser.directive["queue"]
            if isinstance(queue, str):
                queue = json_loads(queue)
                if queue is None:
                    logger.error("Failed to load queue[%s] to json!",
                                 parser.directive)
                    sys.exit(40)

            ret = ACTION_MAP[parser.action](queue)
        else:
            ret = ACTION_MAP[parser.action]()
        sys.exit(ret)
    else:
        logger.error("can not handle the action[%s].", parser.action)
        sys.exit(40)


# usage: queuectl get/add/delete/modify
#   [{
#     "queue_name": xxx,     queue name
#     "default": YES/NO,
#     "minnode": 1,
#     "nodelist": xxx,
#     "allowaccounts": xxx,
#     "denyaccounts": xxx,
#     "state": "UP",
#     "max_time": "INFINITE",
#   }]
if __name__ == "__main__":
    main(sys.argv)
