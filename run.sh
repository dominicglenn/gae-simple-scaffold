#!/usr/bin/env bash

set -e

APP_ID=releasepy-server

if [ ! -d env ]; then
    virtualenv env
fi

source env/bin/activate

case $1 in
"install")
    ./install_deps.py "${@:2}"
    ;;

"start")
    python site-packages/dev/frankenserver/python/dev_appserver.py app.yaml
    ;;

*)
    echo "Error: unknown command!"
    ;;

esac
