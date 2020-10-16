#!/usr/bin/env python

import sys
from os import path
from constants import (
    ACTION_APP_INIT,
    ACTION_APP_START,
    ACTION_APP_STOP,
    ACTION_APP_RESTART,
    ACTION_HEALTH_CHECK,
    ACTION_METADATA_RELOAD,
    ROLE_CONTROLLER,
    ROLE_COMPUTE,
    ROLE_LOGIN,
    SLURM_CONF,
)
from common import (
    logger,
    run_shell,
    get_role,
    ArgsParser,
    get_cluster_info,
)
from host_utils import generate_hosts, set_hostname
from slurm_utils import generate_conf
from softwarectl import init_software
from userctl import add_admin_user

ROLE_SERVICES = {
    ROLE_CONTROLLER: ["slurmctld", "slapd"],
    ROLE_COMPUTE: ["slurmd", "nslcd"],
    ROLE_LOGIN: ["nslcd"],
}
clear_files = {
    ROLE_COMPUTE: ["/usr/sbin/userctl", SLURM_CONF],
    ROLE_LOGIN: ["/usr/sbin/userctl"]
}


def setup():
    logger.info("Generating hosts...")
    generate_hosts()

    logger.info("Setup hostname...")
    set_hostname()
    logger.info("setup done.")
    return 0


def start():
    role = get_role()
    # start before
    if role == ROLE_CONTROLLER:
        logger.info("Generating slurm configurations...")
        generate_conf()
    else:
        for f in clear_files[role]:
            if path.exists(f):
                run_shell("rm {}".format(f))

    # start service
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            logger.info("Start service {}".format(service))
            run_shell("systemctl start {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        return 1

    # start post
    if role == ROLE_CONTROLLER:
        logger.info("create admin dirs..")
        cluster_info = get_cluster_info()
        run_shell("mkdir -p /home/{}/opt".format(cluster_info["admin_user"]))
        run_shell("mkdir -p /home/{}/home/".format(cluster_info["admin_user"]))
        run_shell("mkdir -p /home/{}/data/".format(cluster_info["admin_user"]))

        # create admin user
        add_admin_user()

        # install software
        return init_software()
    logger.info("%s started.", role)
    return 0


def stop():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl stop {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        return 1
    return 0


def restart():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl restart {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        return 1
    logger.info("%s re-started.", role)
    return 0


def check_service_status(service):
    retcode = run_shell("systemctl is-active {}".format(service), without_log=True)
    if retcode != 0:
        logger.error("the service[%s] is not health[code: %s].", service, retcode)
    return retcode


def health_check():
    role = get_role()
    services = ROLE_SERVICES.get(role, "")
    for service in services:
        ret = check_service_status(service)
        if ret != 0:
            return ret
    return 0


def metadata_reload():
    logger.info("generate hosts for reloading..")
    generate_hosts()

    role = get_role()
    if role == ROLE_CONTROLLER:
        logger.info("generate slurm conf for reloading metadata..")
        generate_conf()

        # TODO: 多controller节点时，只在一个master节点执行此命令即可
        logger.info("re-config slurm configuration for cluster..")
        run_shell("systemctl restart slurmctld")
    return 0


def help():
    print "usage: appctl init/start/stop/restart/check/reload"


ACTION_MAP = {
    "help": help,
    "--help": help,
    ACTION_APP_INIT: setup,
    ACTION_APP_START: start,
    ACTION_APP_STOP: stop,
    ACTION_APP_RESTART: restart,
    ACTION_HEALTH_CHECK: health_check,
    ACTION_METADATA_RELOAD: metadata_reload,
}


def main(argv):
    parser = ArgsParser()
    ret = parser.parse(argv)
    if not ret:
        sys.exit(40)

    if parser.action in ACTION_MAP:
        ret = ACTION_MAP[parser.action]()
        sys.exit(ret)
    else:
        logger.error("Un-support action:[%s], exit!", parser.action)
        sys.exit(40)


if __name__ == "__main__":
    main(sys.argv)
