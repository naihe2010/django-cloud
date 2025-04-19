#!/usr/bin/env bash

set -e

original_dir="$(pwd)"
workdir="$(dirname "$(realpath "$0")")"

top_dir="$(dirname "$workdir")"
cd "$top_dir"
poetry build
pip uninstall django-cloud
pip install ./dist/django_cloud-0.1.0-py3-none-any.whl

cd "$workdir/server"
rm -vf /tmp/django_cloud.server.sqlite3
python manage.py migrate
python manage.py createtestdata

cd "$original_dir"