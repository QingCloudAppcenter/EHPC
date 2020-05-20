#!/usr/bin/env python

import subprocess
from constants import *
from datetime import datetime


def run_shell(cmd):
    print "Run cmd[{}]...".format(cmd)
    subprocess.check_call(cmd.split(" "))


# cmd with fmt for time
def backup(cmd):
    run_shell("mkdir -p {}".format(BACKUP_DIR))

    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_shell(cmd.format(now))
