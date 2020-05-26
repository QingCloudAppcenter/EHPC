#!/usr/bin/env python

import subprocess
import requests
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
    res = requests.get(ROLE_URL)
    if res.status_code != 200:
        print "Failed to get role from metadata: {}".format(res.content)
        return False
    return res.text
