#!/usr/bin/env python

import subprocess
from constants import *
from datetime import datetime


def backup(cmd):
    run_shell("mkdir -p {}".format(BACKUP_DIR))
    # cmd with fmt for time
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_shell(cmd.format(now))


def run_shell(cmd):
    print "Run cmd[{}]...".format(cmd)
    subprocess.check_call(cmd.split(" "))


def get_role():
    with open(ROLE_INFO, 'r') as info:
        role = info.read().strip()
    if role:
        print "The role is: {}".format(role)
        return role
    else:
        print "The role is none!"
        exit(1)


def get_hostname():
    role = get_role()
    if role is ROLE_COMPUTE:
        with open(CMP_SID_INFO, "r") as info:
            sid = info.read().strip()
        return "{}{}".format(role, sid)
    else:
        return role
