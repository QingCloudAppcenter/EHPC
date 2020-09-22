#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
import time

from common import logger
from constants import (
    LDAP_ADDRESS,
    LDAP_ROOT_DN,
    LDAP_ADMIN,
    LDAP_ADMIN_PASSWORD,
)

import ldap
from ldap import modlist, UNWILLING_TO_PERFORM

reload(sys)
sys.setdefaultencoding('utf-8')

GROUP_SEARCH_ATTRS = ["gidNumber", "cn"]
USER_SEARCH_ATTRS = ["cn", "uidNumber", "gidNumber", "description"]


class LdapClient(object):
    def __init__(self, ldap_address, root_dn, admin, passwd):
        self.address = ldap_address
        self.bind_dn = "cn={},{}".format(admin, root_dn)
        self.passwd = passwd

        self.user_ou = "People"
        self.user_base_dn = "ou={},{}".format(self.user_ou, root_dn)
        self.user_object_class = [
            "posixAccount",
            "inetOrgPerson",
            "shadowAccount"
        ]

        self.group_ou = "Group"
        self.group_base_dn = "ou={},{}".format(self.group_ou, root_dn)
        self.group_object_class = ["posixGroup"]

        self.ldap_object = None

    def connect(self):
        if self.ldap_object is None:
            logger.info("Connecting ldap server..")
            self.ldap_object = ldap.initialize(self.address)
            self.ldap_object.protocol_version = ldap.VERSION3
            self.ldap_object.set_option(ldap.OPT_REFERRALS, 0)
            self.ldap_object.simple_bind_s(self.bind_dn, self.passwd)
            logger.info("connected.")
        return self.ldap_object

    def close(self):
        if self.ldap_object is not None:
            logger.info("disconnect ldap server..")
            self.ldap_object.unbind_s()
            logger.info("disconnected.")

    def user_dn(self, user_name):
        return "cn={},{}".format(user_name, self.user_base_dn)

    def group_dn(self, group_name):
        return "cn={},{}".format(group_name, self.group_base_dn)

    def create_user(self, user_name, uid, password, home_dir, gid):
        logger.info("create user, home: [%s], name: [%s], uid: [%s], "
                    "gid: [%s], pwd: [%s]", home_dir, user_name, uid,
                    gid, password)
        # create_time is current_time
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        attrs = dict(
            sn=user_name,
            cn=user_name,  # common name
            uid=user_name,
            uidNumber=uid,
            gidNumber=gid,
            userPassword=password,
            ou=self.user_ou,  # People
            homeDirectory=home_dir,
            loginShell="/bin/bash",
            description=create_time,
            objectClass=self.user_object_class  # ['posixAccount','inetOrgPerson'] #cn、sn必填
        )
        ldif = modlist.addModlist(attrs)
        res = self.ldap_object.add_s(self.user_dn(user_name), ldif)
        logger.info("create user response: [%s]", res)

        #创建用户实体先默认不设置密码，直接在创建用户实体设置密码属性，初始密码是未加密形式保存？
        #创建用户实体，设置成密码模式保存
        #password = 'oA@10-14'
        #res = modify_password(dn, None, password)
        #print("modify_password done.")

    def create_group(self, g_name, g_id):
        logger.info("create group, name: [%s], g_id: [%s]", g_name, g_id)
        attrs = dict(
            cn=g_name,  # common name
            memberUid=g_name,
            gidNumber=g_id,
            objectClass=self.group_object_class,
        )
        ldif = modlist.addModlist(attrs)
        res = self.ldap_object.add_s(self.group_dn(g_name), ldif)
        logger.info("Create group response: [%s]", res)

    # ldap search response with default attributes: [
    #     ('ou=People,dc=ehpccloud,dc=com', {'objectClass': ['organizationalUnit'], 'ou': ['People']}),
    #
    #     ('cn=tuser,ou=People,dc=ehpccloud,dc=com',
    #      {'uid': ['tuser'], 'objectClass': ['posixAccount', 'inetOrgPerson', 'shadowAccount'],
    #       'loginShell': ['/bin/bash'], 'userPassword': ['Zhu1241jie'], 'uidNumber': ['1101'], 'gidNumber': ['1101'],
    #       'sn': ['tuser'], 'homeDirectory': ['/home/usr-xxxxx/tuser'], 'ou': ['People'], 'cn': ['tuser']}),
    #
    #     ('cn=tuser2,ou=People,dc=ehpccloud,dc=com',
    #      {'uid': ['tuser2'], 'objectClass': ['posixAccount', 'inetOrgPerson', 'shadowAccount'],
    #       'loginShell': ['/bin/bash'], 'userPassword': ['Zhu1241jie'], 'uidNumber': ['1102'], 'gidNumber': ['1102'],
    #       'sn': ['tuser2'], 'homeDirectory': ['/home/usr-xxxxx/tuser2'], 'ou': ['People'], 'cn': ['tuser2']}),
    # ]
    def list_user(self, user_name=""):
        logger.info("list user ..")
        search_filter = None
        if user_name:
            search_filter = "cn={}".format(user_name)
        ret = self.ldap_object.search_s(self.user_base_dn, ldap.SCOPE_SUBTREE,
                                        search_filter, USER_SEARCH_ATTRS)
        logger.info("search user response: [%s]", ret)
        return ret

    def user_exist(self, user_name, user_id=None):
        logger.info("Check if user[%s %s] exist..", user_name, user_id)
        search_filter = "cn={}".format(user_name)
        ret = self.ldap_object.search_s(
            self.user_base_dn, ldap.SCOPE_SUBTREE,
            search_filter, USER_SEARCH_ATTRS)
        logger.info("Search user name response: [%s]", ret)
        if ret:
            return True

        if user_id:
            logger.info("Check if user id exist..")
            search_filter = "uidNumber={}".format(user_id)
            ret = self.ldap_object.search_s(
                self.user_base_dn, ldap.SCOPE_SUBTREE,
                search_filter, USER_SEARCH_ATTRS)
            logger.info("Search user id response: [%s]", ret)
            if ret:
                return True
        return False

    # search group response: [
    #   ('cn=tuser4,ou=Group,dc=ehpccloud,dc=com', {'gidNumber': ['1000'], 'cn': ['tuser4']})
    # ]
    def group_exist(self, g_id):
        logger.info("Check if group[%s] exist..", g_id)
        search_filter = "gidNumber={}".format(g_id)
        ret = self.ldap_object.search_s(
            self.group_base_dn, ldap.SCOPE_SUBTREE,
            search_filter, GROUP_SEARCH_ATTRS)
        logger.info("Search group id response: [%s]", ret)
        return True if ret else False

    def generate_uid_number(self):
        # generate uid not exist
        users = self.list_user()
        max_uid = 1000
        for user in users:
            for num_str in user[1].get("uidNumber", []):
                num = int(num_str)
                if num > max_uid:
                    max_uid = num
        return str(max_uid + random.randint(1, 100))

    def delete_user(self, user_name):
        logger.info("Delete user[%s]..", user_name)
        dn = "cn={cn},{user_base_dn}".format(
            cn=user_name, ou=self.user_ou, user_base_dn=self.user_base_dn)
        res = self.ldap_object.delete_s(dn)
        logger.info("delete user response: [%s]", res)

    def reset_password(self, user_name, old_password, new_password):
        logger.info("Reset password for user[%s]..", user_name)
        try:
            self.ldap_object.passwd_s(self.user_dn(user_name),
                                      old_password, new_password)
            logger.info("Reset password for user[%s], done.", user_name)
            return 0
        except UNWILLING_TO_PERFORM:
            logger.error("Failed to reset passwd, "
                         "user and password don't match!")
            return 1


def new_ldap_client():
    c = LdapClient(
        LDAP_ADDRESS, LDAP_ROOT_DN, LDAP_ADMIN, LDAP_ADMIN_PASSWORD)
    c.connect()
    return c
