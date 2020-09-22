#!/usr/bin/env python

import sys
import simplejson as jsmod
import traceback

from common import (
    logger,
    json_loads,
    get_cluster_info,
)
from constants import (
    ACTION_USER_ADD,
    ACTION_USER_ADD_ADMIN,
    ACTION_USER_LIST,
    ACTION_USER_DELETE,
    ACTION_RESET_PASSWORD,

    ADMIN_HOME_FMT,
    HOME_FMT,
)
from ldap_utils import new_ldap_client


def get():
    ldap_client = None
    try:
        ldap_client = new_ldap_client()
        ret = ldap_client.list_user()
        # ret format:
        # [('ou=People,dc=ehpccloud,dc=com', {}),
        #
        #  ('cn=admin,ou=People,dc=ehpccloud,dc=com',
        #   {'gidNumber': ['1100'], 'uidNumber': ['1100'], 'cn': ['admin']}),
        #
        #  ('cn=tuser3,ou=People,dc=ehpccloud,dc=com',
        #   {'gidNumber': ['1000'], 'uidNumber': ['1104'], 'cn': ['tuser3'],
        #    'description': ['2020-09-20 14:22:00']})
        # ]

        res = {
            "labels": ["uid", "user", "create_time"],
            "data": [[u[1]["uidNumber"][0], u[1]["cn"][0], u[1].get("description", [""])[0]]
                     for u in ret if u[1].get("cn", None)]
        }
        logger.info("List user: %s", res)
        print jsmod.dumps(res, encoding='utf-8')
    except Exception as e:
        logger.error("list user failed: [%s]", e.message)
        sys.exit(1)
    finally:
        if ldap_client:
            ldap_client.close()


def add(params):
    user_name = params.get("user_name", None)
    password = params.get("password", None)
    if user_name and password:
        ldap_client = None
        try:
            ldap_client = new_ldap_client()
            if ldap_client.user_exist(user_name):
                logger.error("The user[%s] already exist.", user_name)
                sys.exit(45)

            admin_info = get_cluster_info()
            gid = admin_info["group_id"]
            # gname = admin_info["user"]
            # if not ldap_client.group_exist(gid):
            #     ldap_client.create_group(gname, gid)

            uid = ldap_client.generate_uid_number()
            home_dir = get_home_dir(user_name)
            ldap_client.create_user(user_name, uid, password, home_dir, gid)
            logger.info("create user[%s], done.", user_name)
        except Exception:
            logger.error("Failed to create user: [%s]",
                         traceback.format_exc())
            sys.exit(1)
        finally:
            if ldap_client:
                ldap_client.close()
    else:
        logger.error("Require params: user_name: [%s], password: [%s]",
                     user_name, password)
        sys.exit(40)


def add_admin_user():
    ldap_client = new_ldap_client()
    admin_info = get_cluster_info()

    gid = admin_info["group_id"]
    if not ldap_client.group_exist(gid):
        gname = admin_info["user"]
        ldap_client.create_group(gname, gid)

    if not ldap_client.user_exist(admin_info["user"], admin_info["user_id"]):
        home_dir = get_home_dir("", is_admin=True)
        ldap_client.create_user(admin_info["user"],
                                admin_info["user_id"],
                                admin_info["password"], home_dir, gid)
    ldap_client.close()


def delete(params):
    user_name = params.get("user_name", None)
    if not user_name:
        logger.error("required params: user_name[%s].", user_name)
        sys.exit(40)

    if user_name == get_cluster_info()["user"]:
        logger.error("The admin user[%s] can not be deleted.", user_name)
        sys.exit(46)

    ldap_client = None
    try:
        ldap_client = new_ldap_client()
        if not ldap_client.user_exist(user_name):
            logger.error("The user[%s] not exist.", user_name)
            sys.exit(44)

        ldap_client.delete_user(user_name)
        logger.info("The user[%s] has been deleted.", user_name)
    except Exception:
        logger.error("Failed to delete user[%s]: [%s]",
                     user_name, traceback.format_exc())
        sys.exit(1)
    finally:
        if ldap_client:
            ldap_client.close()


def reset_password(params):
    user_name = params.get("user_name", None)
    password = params.get("password", None)
    new_password = params.get("new_password", None)
    logger.info("reset password, user[%s], passwd[%s], new_passwd[%s]",
                user_name, password, new_password)

    if user_name and password and new_password:
        if password == new_password:
            logger.warning("The same password, skip")
            sys.exit(47)

        ldap_client = None
        try:
            ldap_client = new_ldap_client()
            if not ldap_client.user_exist(user_name):
                sys.exit(44)

            ret = ldap_client.reset_password(user_name, password, new_password)
            if ret == 1:
                sys.exit(41)
            logger.info("Reset password, done.")
        except Exception:
            logger.error("Failed reset password of user[%s]: [%s]",
                         user_name, traceback.format_exc())
            sys.exit(1)
        finally:
            if ldap_client:
                ldap_client.close()
    else:
        logger.error("Reset password, lack param.")
        sys.exit(40)


def get_home_dir(user_name, is_admin=False):
    admin_info = get_cluster_info()
    nas_path = admin_info["nas_path"].strip("/")
    if is_admin:
        return ADMIN_HOME_FMT.format(nas_path)
    else:
        return HOME_FMT.format(nas_path, user_name)


def help():
    print "userctl add/get/delete/passwd/add_admin"


def main(argv):
    if len(argv) < 2:
        logger.error("lack param: userctl action {k:v}")
        help()
        sys.exit(40)
    else:
        action = argv[1]

    if action == ACTION_USER_LIST:
        return get()
    elif action == ACTION_USER_ADD_ADMIN:
        add_admin_user()
    elif action in [ACTION_USER_ADD,
                    ACTION_USER_DELETE,
                    ACTION_RESET_PASSWORD]:

        args = json_loads(argv[2])
        if not args:
            logger.error("json load error with params.")
            sys.exit(40)

        if action == ACTION_USER_ADD:
            add(args)
        elif action == ACTION_USER_DELETE:
            delete(args)
        elif action == ACTION_RESET_PASSWORD:
            reset_password(args)
    else:
        logger.error("can not handle the action[%s].", action)
        help()
        sys.exit(40)


# usage: userctl get/add/delete {"user_name": "uxxx", "password": "xxxx"}
if __name__ == "__main__":
    main(sys.argv)
