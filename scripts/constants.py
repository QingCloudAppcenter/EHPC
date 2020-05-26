#!/usr/bin/env python


HOSTS = "/etc/hosts"
WORK_DIR = "/opt/app"
BACKUP_DIR = "{}/backup".format(WORK_DIR)
HOSTS_INFO = "{}/hosts.info".format(WORK_DIR)
HOSTNAME_INFO = "{}/hostname.info".format(WORK_DIR)
RESOURCE_INFO = "{}/resource.info".format(WORK_DIR)
CMP_SID_INFO = "{}/cmp-sid.info".format(WORK_DIR)
CLS_NAME_INFO = "{}/cluster-name.info".format(WORK_DIR)

SLURM_CONF = "/etc/slurm/slurm.conf"
SLURM_CONF_TMPL = "{}/slurm.conf.tmpl".format(WORK_DIR)

BACKUP_HOSTS_CMD = "cp {} {}/hosts_{}.bak".format(HOSTS, BACKUP_DIR, "{}")
BACKUP_SLURM_CONF_CMD = "cp {} {}/slurm.conf_{}.bak".format(SLURM_CONF, BACKUP_DIR, "{}")

ACTION_INIT = "init"
ACTION_START = "start"
ACTION_STOP = "stop"
ACTION_RESTART = "restart"

START_CMDS = {
    "controller": "systemctl start slurmctld",
    "compute": "systemctl start slurmd"
}

ROLE_URL = "http://metadata/self/host/role"
