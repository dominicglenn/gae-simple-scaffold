#!/usr/bin/env bash

set -e

if [ ! -d env ]; then
    virtualenv env
fi

source env/bin/activate

case $1 in
"install")
    ./install_deps.py "${@:2}"
    pip install -r requirements-env.txt
    ;;

"start")
    if [ -d site-packages/dev/frankenserver/ ]; then
        APPENGINE_SERVER_DIR=site-packages/dev/frankenserver/python/

    else
        APPENGINE_SERVER_DIR=site-packages/dev/google_appengine/

    fi

    python $APPENGINE_SERVER_DIR/dev_appserver.py app.yaml
    ;;

*)
    echo "Error: unknown command!"
    ;;

esac
