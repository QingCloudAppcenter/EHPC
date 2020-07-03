#!/usr/bin/env python

import sys
from constants import (
    ACTION_INIT,
    ACTION_START,
    ACTION_STOP,
    ACTION_RESTART,
    START_CMDS,
)
from common import run_shell, get_role
from host_utils import generate_hosts, set_hostname
from slurm_utils import generate_conf


def init():
    print "Generating hosts..."
    generate_hosts()
    print "Setup hostname..."
    set_hostname()
    print "Generating hosts for slurm configurations..."
    generate_conf()
    print "Init done."


def start():
    role = get_role()
    if not role:
        exit(1)
    if role in START_CMDS.keys():
        run_shell(START_CMDS[role])
        print "{} started.".format(role)
    else:
        print "Nothing to do for role[{}].".format(role)


def restart():
    pass


def stop():
    pass


def help():
    print "usage: appctl init/start/stop"


def main(argv):
    if len(argv) < 2:
        help()
        sys.exit(1)
    else:
        action = argv[1]

    if action == ACTION_INIT:
        init()
    elif action == ACTION_START:
        start()
    elif action == ACTION_STOP:
        stop()
    elif action == ACTION_RESTART:
        restart()
    else:
        help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
