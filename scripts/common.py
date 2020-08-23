#!/usr/bin/env python

import sys
import subprocess
from subprocess import Popen, PIPE
from constants import *
from datetime import datetime
import simplejson as jsmod
import traceback


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


def json_load(json_file, err_exit=False):
    try:
        with open(json_file, "r") as fp:
            info = jsmod.load(fp)
        return info
    except Exception:
        print "Failed to load file[%s]: [%s]" % (json_file, traceback.format_exc())
        if err_exit:
            sys.exit(1)
        return None


CLUSTER_INFO = {}


def get_cluster_info():
    global CLUSTER_INFO
    if not CLUSTER_INFO:
        CLUSTER_INFO = json_load(CLS_INFO_FILE, True)
    return CLUSTER_INFO


def get_hostname():
    role = get_role()
    if role == ROLE_COMPUTE:
        sid = get_cluster_info()["sid"]
        return "{}{}".format(COMPUTE_HOSTNAME_PREFIX, sid)
    else:
        return role
