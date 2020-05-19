#!/usr/bin/env bash

set -euxo pipefail

CLS_NAME=`curl http://metadata/self/env/cluster`