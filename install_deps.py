#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import stat
import shutil
import subprocess

from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen


PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

TARGET_DIR = os.path.join(PROJECT_DIR, 'site-packages')

DEV_TARGET_DIR = os.path.join(TARGET_DIR, 'dev')
PROD_TARGET_DIR = os.path.join(TARGET_DIR, 'prod')

REQUIREMENTS_DEV = os.path.join(PROJECT_DIR, 'requirements-dev.txt')
REQUIREMENTS_PROD = os.path.join(PROJECT_DIR, 'requirements-prod.txt')

APPENGINE_TARGET_DIR = os.path.join(DEV_TARGET_DIR, 'google_appengine')
APPENGINE_SDK_VERSION = os.environ.get('SDK_VERSION', '1.9.65')
APPENGINE_SDK_FILENAME = 'google_appengine_%s.zip' % APPENGINE_SDK_VERSION

# Google move versions from 'featured' to 'deprecated' when they bring
# out new releases
SDK_REPO_BASE = 'https://storage.googleapis.com/appengine-sdks'
FEATURED_SDK_REPO = '{0}/featured/'.format(SDK_REPO_BASE)
DEPRECATED_SDK_REPO = '{0}/deprecated/{1}/'.format(
    SDK_REPO_BASE,
    APPENGINE_SDK_VERSION.replace('.', ''),
)

FRANKENSERVER_REPO = 'git@github.com:Khan/frankenserver.git'
FRANKENSERVER_TARGET_DIR = os.path.join(DEV_TARGET_DIR, 'frankenserver')

RESERVED_DEPENDENCIES = (
    'google_appengine',
    'frankenserver',
)


def _download_appengine_sdk():
    # First try and get it from the 'featured' folder
    sdk_file = urlopen(FEATURED_SDK_REPO + APPENGINE_SDK_FILENAME)
    if sdk_file.getcode() == 404:
        # Failing that, 'deprecated'
        sdk_file = urlopen(DEPRECATED_SDK_REPO + APPENGINE_SDK_FILENAME)

    # Handle other errors
    if sdk_file.getcode() >= 299:
        raise Exception(
            'App Engine SDK could not be found. {} returned code {}.'.format(
                sdk_file.geturl(),
                sdk_file.getcode(),
            )
        )

    zipfile = ZipFile(StringIO(sdk_file.read()))
    zipfile.extractall(DEV_TARGET_DIR)


def _clear_dev_dependencies():
    # If we're going to install the App Engine SDK then we can just wipe
    # the entire TARGET_DIR
    if os.path.exists(DEV_TARGET_DIR):
        shutil.rmtree(DEV_TARGET_DIR)


def _install_appengine_sdk():
    _clear_dev_dependencies()

    print('Downloading the AppEngine SDK...')

    _download_appengine_sdk()

    # Make sure the dev_appserver and appcfg are executable
    for module in ('dev_appserver.py', 'appcfg.py'):
        app = os.path.join(APPENGINE_TARGET_DIR, module)
        st = os.stat(app)
        os.chmod(app, st.st_mode | stat.S_IEXEC)


def _execute_args(*args):
    p = subprocess.Popen(args)
    p.wait()


def _install_frankenserver():
    _clear_dev_dependencies()

    _execute_args(
        'git',
        'clone',
        FRANKENSERVER_REPO,
        os.path.join(DEV_TARGET_DIR, 'frankenserver'),
    )

    _execute_args(
        'pip',
        'install',
        '-r',
        os.path.join(DEV_TARGET_DIR, 'frankenserver', 'requirements.txt'),
    )


def _clear_dependencies(target_dir):
    for name in os.listdir(target_dir):
        if name in RESERVED_DEPENDENCIES:
            continue

        path = os.path.join(target_dir, name)

        try:
            shutil.rmtree(path)

        except OSError:
            os.unlink(path)


def _install_dependencies(requirements_file, target_dir):
    _execute_args(
        'pip',
        'install',
        '--no-deps',
        '-r', requirements_file,
        '-t', target_dir,
        '-I',
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Dependency installer',
    )

    parser.add_argument(
        '--install-sdk',
        action='store_true',
    )

    parser.add_argument(
        '--frankenserver',
        action='store_true',
    )

    parser.add_argument(
        '--clear',
        action='store_true',
    )

    arguments = parser.parse_args()

    if arguments.install_sdk or not (
        os.path.exists(APPENGINE_TARGET_DIR)
        or os.path.exists(FRANKENSERVER_TARGET_DIR)
    ):
        if arguments.frankenserver:
            _install_frankenserver()

        else:
            _install_appengine_sdk()

    elif arguments.clear:
        print('Clearing dependencies...')
        _clear_dependencies(DEV_TARGET_DIR)
        _clear_dependencies(PROD_TARGET_DIR)

    print('Running pip...')

    _install_dependencies(REQUIREMENTS_DEV, DEV_TARGET_DIR)
    _install_dependencies(REQUIREMENTS_PROD, PROD_TARGET_DIR)
