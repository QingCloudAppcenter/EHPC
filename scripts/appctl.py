#!/usr/bin/env python

import sys
import requests
from constants import (
    ACTION_INIT,
    ACTION_START,
    ACTION_STOP,
    ACTION_RESTART,
    ROLE_URL,
    START_CMDS,
)
from common import run_shell
from hosts import generate
from slurm import generate_conf


def init():
    print "Generating hosts for cluster..."
    generate()
    print "Generating hosts for slurm configurations..."
    generate_conf()
    print "Init done."


def start():
    res = requests.get(ROLE_URL)
    if res.status_code != 200:
        print "Failed to get role from metadata: {}".format(res.content)
        exit(1)
    role = res.text
    if role in START_CMDS.keys():
        run_shell(START_CMDS[role])
        print "{} started.".format(role)
    else:
        print "Nothing to start for role[{}].".format(role)


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
