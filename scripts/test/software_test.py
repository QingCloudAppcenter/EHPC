#!/usr/bin/env python

import sys

from ehpc.scripts.common import (
    logger,
    ArgsParser,
)
from ehpc.scripts.constants import (
    ACTION_SOFTWARE_INSTALL,
    ACTION_SOFTWARE_UNINSTALL,
    ACTION_RESET_PASSWORD,
)

SOFTWARE_WORKDIR = "/tmp/software"
SOFTWARE_HOME_FMT = "/home/{}/opt"


# software format:
#   [{
#     "name": xxx,     name must be same as install dir and dir after un-tar
#     "source": xxx,
#     "installer": xxx, Run: [SOFTWARE_HOME]/[installer]
#   }]
def install(software):
    logger.info("install software[%s]..", software)


def reset(software):
    logger.info("reset software[%s]..", software)


# software format:
#   [{
#     "name": xxx,     name must be same as install dir and dir after un-tar
#     "uninstaller": xxx
#   }]
def uninstall(software):
    logger.info("uninstall software[%s]..", software)


def help():
    print "softwarectl install [{name: xxx, source: xxx, installer: xxxx}, ..]\n"
    print "            uninstall [{name: xxxx, uninstaller: xxx}]\n"


ACTION_MAP = {
    "help": help,
    "--help": help,
    ACTION_SOFTWARE_INSTALL: install,
    ACTION_SOFTWARE_UNINSTALL: uninstall,
    ACTION_RESET_PASSWORD: reset,
}


# could use env [SOFTWARE_HOME] in install or uninstall script
def main(argv):
    parser = ArgsParser()
    ret = parser.parse(argv)
    if not ret:
        logger.error("Failed parse param: [%s]", argv[1:])
        sys.exit(40)

    if parser.action in ACTION_MAP:
        ACTION_MAP[parser.action](parser.directive) if parser.directive \
            else ACTION_MAP[parser.action]()
    else:
        logger.error("can not handle the action[%s].", parser.action)
        sys.exit(40)


if __name__ == "__main__":
    main(sys.argv)
