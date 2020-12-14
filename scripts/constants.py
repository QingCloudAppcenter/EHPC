#!/usr/bin/env python

# appctl constants
HOSTS = "/etc/hosts"
APP_HOME = "/opt/app"
APP_CONF_DIR = "{}/conf".format(APP_HOME)
BACKUP_DIR = "{}/backup".format(APP_HOME)
LOG_DIR = "{}/log".format(APP_HOME)

LOG_FILE = "{}/ehpc.log".format(LOG_DIR)
LOG_DEBUG_FLAG = "{}/debug.flag".format(APP_CONF_DIR)

HOSTS_INFO_FILE = "{}/hosts.info".format(APP_CONF_DIR)
RESOURCE_INFO_FILE = "{}/resource.info".format(APP_CONF_DIR)
CLUSTER_INFO_FILE = "{}/cluster.info".format(APP_CONF_DIR)

SLURM_CONF = "/etc/slurm/slurm.conf"
SLURM_CONF_TMPL = "{}/tmpl/slurm.conf.tmpl".format(APP_HOME)
NODE_RESOURCE_FMT = "NodeName={} {}"
PARTITION_CONF_FMT = "PartitionName={} Default={} MinNodes={} AllowGroups=ALL "\
                     "PriorityJobFactor=1 PriorityTier=1 DisableRootJobs=NO "\
                     "RootOnly=NO Hidden=NO Shared=NO GraceTime=0 "\
                     "PreemptMode=OFF ReqResv=NO AllowAccounts={} "\
                     "AllowQos=ALL LLN=NO ExclusiveUser={} OverSubscribe=NO "\
                     "OverTimeLimit=0 State={} Nodes={}"

HPC_MODULE_FILES = "/opt/modules-4.6.0/modulefiles/hpcmodulefiles"
HPC_MODULE_FILES_TMPL = "{}/tmpl/hpcmodulefiles.tmpl".format(APP_HOME)
HPC_DEFAULT_MODULE_FILE = "{}/tmpl/default-modulefile".format(APP_HOME)

BACKUP_HOSTS_CMD = "cp {} {}/hosts_{}.bak".format(HOSTS, BACKUP_DIR, "{}")
BACKUP_SLURM_CONF_CMD = "cp {} {}/slurm.conf_{}.bak".format(SLURM_CONF, BACKUP_DIR, "{}")

LOGIN_HOSTNAME_PREFIX = "login"
CONTROLLER_HOSTNAME_PREFIX = "controller"
COMPUTE_HOSTNAME_PREFIX = "node"
HOST_PREFIX = "host"

ADMIN_HOME_FMT = "{}/home/admin"  # {nas_mount_point}//home/admin
HOME_FMT = "{}/home/{}"  # {nas_mount_point}/home/user_name
SOFTWARE_INFO = "{}/software.info".format(APP_CONF_DIR)


LDAP_ADDRESS = "ldap://controller:389"
LDAP_ROOT_DN = "dc=ehpccloud,dc=com"
LDAP_ADMIN = "ldapadm"
LDAP_ADMIN_PASSWORD = "Zhu1241jie"
LDAP_CONNECT_RETRY = 5

ROLE_CONTROLLER = "controller"
ROLE_COMPUTE = "compute"
ROLE_LOGIN = "login"
MASTER_CONTROLLER_SID = 1

ACTION_APP_INIT = "init"
ACTION_APP_START = "start"
ACTION_APP_STOP = "stop"
ACTION_APP_RESTART = "restart"
ACTION_HEALTH_CHECK = "check"
ACTION_METADATA_RELOAD = "reload"

# userctl constants
ACTION_USER_LIST = "list"
ACTION_USER_ADD = "add"
ACTION_USER_ADD_ADMIN = "add_admin"
ACTION_USER_DELETE = "delete"
ACTION_RESET_PASSWORD = "reset_passwd"

# softwarectl constants
ACTION_SOFTWARE_INSTALL = "install"
ACTION_SOFTWARE_UNINSTALL = "uninstall"

# Partition attribution
DEFAULT = "Default"
NODES = "Nodes"
PARTITION_NAME = "PartitionName"
NODEID_LIST = "NodeidList"
MIN_MODES = "MinNodes"
ALLOW_ACCOUNTS = "AllowAccounts"
EXCLUSIVE_USER = "ExclusiveUser"
STATE = "State"
NODEID_LIST = "NodeidList"
PARTITION_CONTROLLER = "controller"
# queuectl constants
ACTION_QUEUE_ADD = "add_queue"
ACTION_QUEUE_GET = "get_queue"
ACTION_QUEUE_DELETE = "del_queue"
ACTION_QUEUE_MODIFY = "modify_queue"

# timeout
ACTION_GET_TIMEOUT = 60
ACTION_SET_TIMEOUT = 60

ACTION_PARAM_CONF = {
    # userctl
    ACTION_USER_ADD: {
        "type": dict,
        "children": {
            "user_name": {
                "type": str,
                "required": True
            },
            "password": {
                "type": str,
                "required": True
            }
        }
    },
    ACTION_RESET_PASSWORD: {
        "type": dict,
        "children": {
            "username": {
                "type": str,
                "required": True
            },
            "password": {
                "type": str,
                "required": True
            },
            "new_password": {
                "type": str,
                "required": False
            }
        }
    },
    ACTION_USER_DELETE: {
        "type": dict,
        "children": {
            "user_name": {
                "type": str,
                "required": True
            }
        }
    },

    # softwarectl
    ACTION_SOFTWARE_INSTALL: {
        "type": dict,
        "children": {
            "software": {
                "type": list,
                "required": True,
                "children": {
                    "type": dict,
                    "children": {
                        "name": {
                            "type": str,
                            "required": True
                        },
                        "version": {
                            "type": str,
                            "required": True
                        },
                        "source": {
                            "type": str,
                            "required": True
                        },
                        "installer": {
                            "type": str,
                            "required": False
                        }
                    }
                }
            }
        }
    },
    ACTION_SOFTWARE_UNINSTALL: {
        "type": dict,
        "children": {
            "software": {
                "type": list,
                "required": True,
                "children": {
                    "type": dict,
                    "children": {
                        "name": {
                            "type": str,
                            "required": True
                        },
                        "version": {
                            "type": str,
                            "required": True
                        },
                        "uninstaller": {
                            "type": str,
                            "required": False
                        }
                    }
                }
            }
        }
    },

    # queuectl
    ACTION_QUEUE_GET: {
        "type": dict,
        "children": {
            "queue": {
                "type": list,
                "required": True,
                "children": {
                    "type": dict,
                    "children": {
                        "queue_name": {
                            "type": str,
                            "required": True
                        }
                    }
                }
            }
        }
    },
    ACTION_QUEUE_DELETE: {
        "type": dict,
        "children": {
            "software": {
                "type": list,
                "required": True,
                "children": {
                    "type": dict,
                    "children": {
                        "queue_name": {
                            "type": str,
                            "required": True
                        }
                    }
                }
            }
        }
    },
    ACTION_QUEUE_ADD: {
        "type": dict,
        "children": {
            "software": {
                "type": list,
                "required": True,
                "children": {
                    "type": dict,
                    "children": {
                        "queue_name": {
                            "type": str,
                            "required": True
                        },
                        "default": {
                            "type": str,
                            "required": True
                        },
                        "minnode": {
                            "type": int,
                            "required": False
                        },
                        "nodelist": {
                            "type": str,
                            "required": True
                        },
                        "allowaccounts": {
                            "type": str,
                            "required": False
                        },
                        "denyaccounts": {
                            "type": str,
                            "required": False
                        },
                        "state": {
                            "type": str,
                            "required": False
                        },
                        "max_time": {
                            "type": str,
                            "required": False
                        }
                    }
                }
            }
        }
    },
    ACTION_QUEUE_MODIFY: {
        "type": dict,
        "children": {
            "software": {
                "type": list,
                "required": True,
                "children": {
                    "type": dict,
                    "children": {
                        "queue_name": {
                            "type": str,
                            "required": True
                        },
                        "default": {
                            "type": str,
                            "required": True
                        },
                        "minnode": {
                            "type": int,
                            "required": False
                        },
                        "nodelist": {
                            "type": str,
                            "required": True
                        },
                        "allowaccounts": {
                            "type": str,
                            "required": False
                        },
                        "denyaccounts": {
                            "type": str,
                            "required": False
                        },
                        "state": {
                            "type": str,
                            "required": False
                        },
                        "max_time": {
                            "type": str,
                            "required": False
                        }
                    }
                }
            }
        }
    },
}
