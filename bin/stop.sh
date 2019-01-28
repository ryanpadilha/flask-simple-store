#!/bin/bash
#
# This script stop python application using Gunicorn

echo "stop python application"

PID=$(cat /var/named/run/gunicorn-simple.pid)
kill -9 $PID
