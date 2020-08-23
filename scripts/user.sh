#!/usr/bin/env bash

NAME=$1
PASSWORD=$2
ADMIN_UID=$3
G_NAME=$1
ADMIN_GID=$4
NAS_PATH=$5


cat /etc/group | grep ${ADMIN_GID}
e1=`echo $?`

if [[ ${e1} == 1 ]];then
  echo "Create group[${ADMIN_GID}][${G_NAME}] .."
  groupadd -g ${ADMIN_GID} ${G_NAME}
else
  echo "Group[${ADMIN_GID}][${G_NAME}] exist."
fi


cat /etc/passwd |grep ${NAME}
e2=`echo $?`
if [[ ${e1} == 1 ]];then
  echo "Create user[${ADMIN_UID}][${NAME}][${NAS_PATH}] .."

  if [[ $NAS_PATH == \/* ]]; then
      USER_HOME="/home${NAS_PATH}"
  else
      USER_HOME="/home/${NAS_PATH}"
  fi

  useradd -d ${USER_HOME} -u ${ADMIN_UID} -g ${ADMIN_GID} -m ${NAME}
  echo ${PASSWORD} |passwd --stdin ${NAME}
else
  echo "User[${ADMIN_UID}][${NAME}] exist."
fi

echo "User operate, done."
