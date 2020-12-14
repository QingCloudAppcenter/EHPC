#!/usr/bin/env python

import os
import sys
import crypt
from os import path
from constants import (
    ACTION_APP_INIT,
    ACTION_APP_START,
    ACTION_APP_STOP,
    ACTION_APP_RESTART,
    ACTION_HEALTH_CHECK,
    ACTION_METADATA_RELOAD,
    ACTION_RESET_PASSWORD,
    ROLE_CONTROLLER,
    ROLE_COMPUTE,
    ROLE_LOGIN,
    SLURM_CONF,
    MASTER_CONTROLLER_SID,
)
from common import (
    logger,
    run_shell,
    get_role,
    ArgsParser,
    get_cluster_info,
    get_nas_mount_point,
    get_cluster_name,
)


def add_user(username, password, uid, gid, nas_mount_path=None):
    run_shell("groupadd -g %s %s" % (gid, username))
    salt = ''.join(map(lambda x:
                       './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'[
                           ord(x) % 64], os.urandom(16)))
    pwd = crypt.crypt(password, "$6$%s" % salt)
    pwd = pwd.replace("$", "\$")

    run_shell("useradd -u %s -g %s -p %s %s" %
              (uid, gid, pwd, username))
    # run_shell("chmod 755 /etc/sudoers")
    # run_shell("cat >> /etc/sudoers <<EOF\n%s   ALL=(ALL)      NOPASSWD: ALL\nEOF" %
    #           username)
    # run_shell("chmod 755 /etc/sudoers")
    run_shell("usermod -aG wheel %s" % username)

def modify_user_password(username, old_password, password):
    salt = ''.join(map(lambda x:
                       './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'[
                           ord(x) % 64], os.urandom(16)))
    pwd = crypt.crypt(password, "$6$%s" % salt)
    pwd = pwd.replace("$", "\$")
    run_shell("usermod -p %s %s" % (pwd, username))

def setup():
    logger.info("initialize cluster...")
    cluster_info = get_cluster_info()
    username = cluster_info.get("user")
    password = cluster_info.get("password")
    gid = cluster_info.get("gid")
    uid = cluster_info.get("uid")
    # create user
    add_user(username, password, uid, gid)
    logger.info("setup done.")
    return 0


def metadata_reload():
    logger.info("cluster metadata reload...")
    cluster_info = get_cluster_info()
    username = cluster_info.get("user")
    password = cluster_info.get("password")
    gid = cluster_info.get("gid")
    uid = cluster_info.get("uid")
    # create user
    add_user(username, password, uid, gid)
    logger.info("setup done.")
    return 0


def reset_password(params):
    username = params.get("username", None)
    password = params.get("password", None)
    new_password = params.get("new_password", None)
    logger.info("reset password, user[%s], passwd[%s], new_passwd[%s]",
                username, password, new_password)
    # create admin user
    modify_user_password(username, password, new_password)
    logger.info("reset password done.")
    return 0


def help():
    print "usage: appctl init/start/stop/restart/check/reload"


ACTION_MAP = {
    "help": help,
    "--help": help,
    ACTION_APP_INIT: setup,
    ACTION_METADATA_RELOAD: metadata_reload,
    ACTION_RESET_PASSWORD: reset_password,
}


def main(argv):
    parser = ArgsParser()
    ret = parser.parse(argv)
    if not ret:
        sys.exit(40)

    if parser.action in ACTION_MAP:
        # ret = ACTION_MAP[parser.action]()
        ret = ACTION_MAP[parser.action](parser.directive) if parser.directive \
            else ACTION_MAP[parser.action]()
        sys.exit(ret)
    else:
        logger.error("Un-support action:[%s], exit!", parser.action)
        sys.exit(40)


if __name__ == "__main__":
    main(sys.argv)
