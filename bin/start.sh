#!/bin/bash

# This script start python application using Gunicorn

set -e # if occur any error, exit

function to_console {
    echo -e "\n*** $1 ***\n"
}

cd $(dirname $0) && cd ..

to_console "activate virtual environment sandbox"
source venv-sandbox/bin/activate

PID=/var/named/run/gunicorn-simple.pid
if [ -f $PID ]; then rm $PID; fi

to_console "start python application"
exec gunicorn -w 3 --bind=0.0.0.0:8000 --user=ubuntu --log-level=debug --pid=$PID --log-file=/var/named/logs/sapiensx.com.br/gunicorn.log 2>>/var/named/logs/sapiensx.com.br/gunicorn.log wsgi:application &