#!/usr/bin/env python

import sys
from os import path
from constants import (
    ACTION_APP_INIT,
    ACTION_APP_START,
    ACTION_APP_STOP,
    ACTION_APP_RESTART,
    ACTION_HEALTH_CHECK,
    ACTION_USER_ADD_ADMIN,
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
)
from host_utils import generate_hosts, set_hostname
from slurm_utils import generate_conf

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


def start():
    role = get_role()
    # start before
    if role == ROLE_CONTROLLER:
        logger.info("Generating hosts for slurm configurations...")
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
        sys.exit(1)

    # start post
    if role == ROLE_CONTROLLER:
        # create admin user
        run_shell("userctl {}".format(ACTION_USER_ADD_ADMIN))
    logger.info("%s started.", role)


def stop():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl stop {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        sys.exit(1)


def restart():
    role = get_role()
    if role in ROLE_SERVICES:
        for service in ROLE_SERVICES[role]:
            run_shell("systemctl restart {}".format(service))
    else:
        logger.error("Un-support role[%s].", role)
        sys.exit(1)
    logger.info("%s re-started.", role)


def check_service_status(service):
    retcode = run_shell("systemctl is-active {}".format(service), without_log=True)
    if retcode != 0:
        logger.error("the {} service is not health.".format(service))
        sys.exit(retcode)
    return retcode


def health_check():
    role = get_role()
    services = ROLE_SERVICES.get(role, "")
    for service in services:
        check_service_status(service)
    sys.exit(0)


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


def help():
    print "usage: appctl init/start/stop/restart/check/reload"


ACTION_MAP = {
    ACTION_APP_INIT: setup,
    ACTION_APP_START: start,
    ACTION_APP_STOP: stop,
    ACTION_APP_RESTART: restart,
    ACTION_HEALTH_CHECK: health_check,
    ACTION_METADATA_RELOAD: metadata_reload,
}


def main(argv):
    if len(argv) < 2:
        help()
        sys.exit(1)
    else:
        action = argv[1]

    if action in ACTION_MAP:
        ACTION_MAP[action]()
    else:
        logger.error("Un-support action:[%s], exist!", action)
        help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
