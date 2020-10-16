#!/usr/bin/env python

import os
import sys
import traceback

from common import (
    logger,
    ArgsParser,
    run_shell,
    get_admin_user,
    json_load,
    json_loads,
)
from constants import (
    SOFTWARE_INFO,
    ACTION_PARAM_CONF,
    ACTION_SOFTWARE_INSTALL,
    ACTION_SOFTWARE_UNINSTALL,

)

SOFTWARE_WORKDIR_FMT = "/home/{}/tmp/software/{}"
SOFTWARE_HOME_FMT = "/home/{}/opt"


def init_software():
    # install software
    software = json_load(SOFTWARE_INFO)
    if software is None:
        logger.error("The software info is invalid format!")
        return 40

    logger.info("init: install software[%s]..", software)
    if software:
        p_conf = ACTION_PARAM_CONF[ACTION_SOFTWARE_INSTALL]["children"]["software"]
        if not ArgsParser.check("software", software, p_conf):
            logger.error("The software[%s] valid failed!", software)
            return 40
        return install(software, ignore_exist=True)
    return 0


# software format:
#   [{
#     "name": xxx,     software name
#     "source": xxx,
#     "installer": xxx, Run: [SOFTWARE_HOME]/[installer]
#   }]
def install(software_list, ignore_exist=False):
    logger.info("install software[%s]..", software_list)
    software_home = SOFTWARE_HOME_FMT.format(get_admin_user())
    if software_list:
        run_shell("mkdir -p {}".format(software_home))

    exist_info = {}
    for s in software_list:
        # software exist
        if os.path.exists("{}/{}".format(software_home, s["name"])):
            exist_info[s["name"]] = True
            logger.error("The software[%s] already exist!", s["name"])
            if not ignore_exist:
                return 55

    for s in software_list:
        if not exist_info.get(s["name"], False):
            ret = _install(s["name"], s["source"], software_home,
                           s.get("installer"))
            if ret is not 0:
                return ret
    return 0


def _download(source, workdir):
    if source.startswith("http"):
        run_shell("wget -P {} -t 5 -w 60 -c {}".format(workdir, source), timeout=600)
    else:
        run_shell("rsync -q -aP {} {}/".format(source, workdir), timeout=600)


def _install(software, source, software_home, installer=None):
    """
    :param source: full url to download software, eg: root@xxx/aa/bb/cc.tar.gz
    :param software_home: the home that software would to be installed
    :param software: software name (install dir: software_home/software)
    :param installer: install script
    :return:
    """
    logger.info("Do install software[%s] from source[%s]..", software, source)

    package = source.split("/")[-1]
    workdir = SOFTWARE_WORKDIR_FMT.format(get_admin_user(), software)
    package_path = "{}/{}".format(workdir, package)

    try:
        # download
        _download(source, workdir)

        # un-tar
        run_shell("tar -zxf {}".format(package_path), cwd=workdir, timeout=180)

        # install
        ret = os.listdir(workdir)
        un_tar_dir = ""
        for r in ret:
            if os.path.isdir("{}/{}".format(workdir, r)):
                un_tar_dir = "{}/{}".format(workdir, r)
                break

        if installer:
            installer = "bash {}/{}".format(un_tar_dir, installer)
        else:
            f = "bash {}/install.sh".format(un_tar_dir)
            installer = f if os.path.exists(f) else \
                "mv {} {}/".format(un_tar_dir, software_home)

        run_shell("export SOFTWARE_HOME={} && {}".format(software_home, installer), timeout=120)

        # clean
        if os.path.exists(workdir):
            run_shell("rm -rf {}".format(workdir))
    except Exception:
        logger.error("Failed to install software[%s]: \n%s",
                     software, traceback.format_exc())
        return 1
    return 0


# software format:
#   [{
#     "name": xxx,     name must be same as install dir and dir after un-tar
#     "uninstaller": xxx
#   }]
def uninstall(software):
    logger.info("uninstall software[%s]..", software)
    software_home = SOFTWARE_HOME_FMT.format(get_admin_user())
    for s in software:
        if not os.path.exists("{}/{}".format(software_home, s["name"])):
            logger.error("The software[%s] not exist!", s["name"])
            return 54

    for s in software:
        ret = _uninstall(s["name"], software_home, s.get("uninstaller"))
        if ret is not 0:
            return ret
    return 0


def _uninstall(software, software_home, uninstaller=None):
    logger.info("Do uninstall software[%s]..", software)
    software_dir = "{}/{}".format(software_home, software)
    if uninstaller:
        uninstaller = "bash {}".format(uninstaller)
    else:
        f = "bash {}/uninstall.sh".format(software_dir)
        uninstaller = f if os.path.exists(f) else "rm -rf {}".format(software_dir)

    try:
        # uninstall
        run_shell("export SOFTWARE_HOME={} && {}".format(software_home, uninstaller))
    except Exception as e:
        logger.error("Failed to run install cmd: %s", e.message)
        logger.error("Error: %s", traceback.format_exc())
        return 1
    return 0


def help():
    print "softwarectl install [{name: xxx, source: xxx, installer: xxxx}, ..]\n"
    print "            uninstall [{name: xxxx, uninstaller: xxx}]\n"


ACTION_MAP = {
    "help": help,
    "--help": help,
    ACTION_SOFTWARE_INSTALL: install,
    ACTION_SOFTWARE_UNINSTALL: uninstall,
    "init": init_software,  # testing
}


# could use env [SOFTWARE_HOME] in install or uninstall script
def main(argv):
    try:
        parser = ArgsParser()
        ret = parser.parse(argv)
        if not ret:
            sys.exit(40)

        if parser.action in ACTION_MAP:
            if parser.directive:
                software = parser.directive["software"]
                if isinstance(software, str):
                    software = json_loads(software)
                    if software is None:
                        logger.error("Failed to load software[%s] to json!",
                                     parser.directive)
                        sys.exit(40)

                ret = ACTION_MAP[parser.action](software)
            else:
                ret = ACTION_MAP[parser.action]()
            sys.exit(ret)
        else:
            logger.error("can not handle the action[%s].", parser.action)
            sys.exit(40)
    except Exception:
        logger.error("Failed to update software: [%s]", traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
