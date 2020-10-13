#!/usr/bin/env python

import sys
import subprocess
import traceback
import simplejson as jsmod
from datetime import datetime
from os import path as os_path
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    CLUSTER_INFO_FILE,
    BACKUP_DIR,
    LOG_DIR,
    LOG_FILE,
    COMPUTE_HOSTNAME_PREFIX,
    ROLE_COMPUTE,
    ACTION_PARAM_CONF,
)

# create log dir
if not os_path.exists(LOG_DIR):
    subprocess.check_call("mkdir -p {}".format(LOG_DIR).split(" "))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formater = logging.Formatter(
    '[%(asctime)s] - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]')
ehpc_handler = RotatingFileHandler(LOG_FILE, mode="w", maxBytes=100000000,
                                   backupCount=3, encoding="utf-8")
ehpc_handler.setFormatter(formater)
ehpc_handler.setLevel(logging.DEBUG)

logger.addHandler(ehpc_handler)

CLUSTER_INFO = {}


def backup(cmd):
    run_shell("mkdir -p {}".format(BACKUP_DIR))
    # cmd with fmt for time
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_shell(cmd.format(now))


def run_shell(cmd, without_log=False):
    if not without_log:
        logger.info("Run cmd[%s]...", cmd)
    return subprocess.check_call(cmd.split(" "))


def json_load(json_file, err_exit=False):
    try:
        with open(json_file, "r") as fp:
            info = jsmod.load(fp)
        return info
    except Exception:
        logger.error("Failed to load file[%s]: [%s]", json_file,
                     traceback.format_exc())
        if err_exit:
            sys.exit(1)
        return None


def json_loads(json_str):
    try:
        return jsmod.loads(json_str, encoding='utf-8')
    except Exception:
        logger.error("loads json str[%s] error: %s",
                     json_str, traceback.format_exc())
        return None


def get_cluster_info():
    global CLUSTER_INFO
    if not CLUSTER_INFO:
        CLUSTER_INFO = json_load(CLUSTER_INFO_FILE, True)
    return CLUSTER_INFO


def get_role():
    cluster_info = get_cluster_info()
    role = cluster_info.get("role")
    if role:
        return role
    else:
        logger.error("The role is none!")
        sys.exit(1)


def get_hostname():
    role = get_role()
    if role == ROLE_COMPUTE:
        cluster_info = get_cluster_info()
        return "{}{}".format(COMPUTE_HOSTNAME_PREFIX, cluster_info["sid"])
    else:
        return role


class ArgsParser(object):

    def __init__(self):
        self.action = ""
        self.directive = {}

    def parse(self, args):
        logger.info("parse args: [%s]", args)
        if len(args) < 1:
            logger.error("parameter[%s] is not complete(action needed)!")
            return False

        self.action = args[0]
        if len(args) > 1:
            self.directive = json_loads(args[1]) or {}
        logger.debug("directive: [%s]", self.directive)
        return self._check()

    def _check(self):
        if self.action in ACTION_PARAM_CONF:
            conf = ACTION_PARAM_CONF[self.action]
            return ArgsParser._check_dict_param("ALL", self.directive, conf)
        else:
            self.directive = {}  # clear directive that there is no param
        return True

    @staticmethod
    def check(param, v, param_conf):
        logger.debug("check--> p: [%s] v: [%s], conf: [%s]", param, v, param_conf)
        ret = False
        p_type = param_conf["type"]
        if p_type == "str":
            ret = ArgsParser._check_str_param(param, v, param_conf)
        elif p_type == "list":
            ret = ArgsParser._check_list_param(param, v, param_conf)
        elif p_type == "dict":
            ret = ArgsParser._check_dict_param(param, v, param_conf["children"])
        else:
            logger.error("un-support param type[%s] of param[%s], conf: [%s]",
                         p_type, param, param_conf)
        return ret

    @staticmethod
    def _check_str_param(param, str_v, param_conf):
        logger.debug("check_str--> p: [%s] v: [%s], conf: [%s]", param, str_v, param_conf)
        if param_conf["required"] and str_v is None:
            logger.error("miss value[%s] of param[%s]", str_v, param)
            return False

        if str_v is not None and \
                (not isinstance(str_v, str)) and \
                (not isinstance(str_v, unicode)):
            logger.error("value[%s] of param[%s] should be string", str_v, param)
            return False
        return True

    @staticmethod
    def _check_list_param(param, list_v, param_conf):
        logger.debug("check_list--> p: [%s] v: [%s], conf: [%s]", param, list_v, param_conf)
        # check required
        if param_conf.get("required") and list_v is None:
            logger.error("miss value[%s] of param[%s]", list_v, param)
            return False

        # check value type
        if not isinstance(list_v, list):
            logger.error("value[%s] of param[%s] should be list",
                         list_v, param)
            return False

        # check children
        for v in list_v:
            ret = ArgsParser.check(param, v, param_conf["children"])
            if not ret:
                return False
        return True

    @staticmethod
    def _check_dict_param(param, dict_v, param_conf):
        logger.debug("check_dict--> p: [%s] v: [%s], conf: [%s]", param, dict_v, param_conf)
        # check required
        if dict_v is None:
            logger.error("miss value[%s] of param[%s]", dict_v, param)
            return False

        # check value type
        if not isinstance(dict_v, dict):
            logger.error("value[%s] of param[%s] for param_conf[%s] should be dict",
                         dict_v, param, param_conf)
            return False

        # check children
        for p, conf in param_conf.items():
            ret = ArgsParser.check(p, dict_v.get(p), conf)
            if not ret:
                return ret
        return True
