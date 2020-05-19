#!/usr/bin/env bash

set -euxo pipefail

HOSTS="/etc/hosts"
EHPC_HOSTS_INFO="/opt/qingcloud/ehpc-hosts.info"
HOSTS_BAK_DIR="/opt/qingcloud/hosts-bak"
HOSTS_BAK="${HOSTS_BAK_DIR/hosts_`date -Iseconds`.bak"

mkdir -p ${HOST_BAK_DIR}
LINE_NO=`grep -n "metadata" ${HOSTS} | cut -d ":" -f 1`
cp ${HOSTS} ${HOSTS_BAK}
head -${LINE_NO} ${HOSTS_BAK} > ${HOSTS}
cat ${EHPC_HOSTS_INFO} >> ${HOSTS}
