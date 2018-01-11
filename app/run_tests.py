#!/usr/bin/env python
import sys
import unittest
import os
import logging

import nose


USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to Google Cloud or Google App Engine SDK installation, usually ~/google_cloud_sdk
TEST_PATH   Path to package containing test modules"""

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ['DISABLE_CONFIG_ENTITY_INIT'] = '1'


class CustomTestLoader(unittest.loader.TestLoader):
    def _get_module_from_name(self, name):
        # this is to make sure that gae and gae sdk paths are looked up first, since they
        # are assumed to be top level when running the gae app, even though it is not top-level
        if sys.path[0] == BASE_DIR:
            sys.path.pop(0)
            sys.path.insert(0, os.path.join(BASE_DIR, 'gae'))

        if name.startswith('gae.'):
            name = name[len('gae.'):]

        __import__(name)
        return sys.modules[name]


def main(sdk_path):
    # If the sdk path points to a google cloud sdk installation
    # then we should alter it to point to the GAE platform location.
    if os.path.exists(os.path.join(sdk_path, 'platform/google_appengine')):
        sys.path.insert(0, os.path.join(sdk_path, 'platform/google_appengine'))
    else:
        sys.path.insert(0, sdk_path)

    sys.path.append(
        os.path.join(BASE_DIR, 'third_party', 'py'),
    )

    # Ensure that the google.appengine.* packages are available
    # in tests as well as all bundled third-party packages.
    import dev_appserver
    dev_appserver.fix_sys_path()

    sys.path.insert(
        0,
        os.path.join(BASE_DIR, 'env', 'lib', 'python2.7', 'site-packages')
    )

    # Loading appengine_config from the current project ensures that any
    # changes to configuration there are available to all tests (e.g.
    # sys.path modifications, namespaces, etc.)
    try:
        import appengine_config
    except ImportError:
        logging.warning("Note: unable to import appengine_config.")

    # Discover and run tests.
    os.environ['NOSE_COVER_PACKAGE'] = 'handlers,lib,models,services'
    suite = CustomTestLoader().discover('.', pattern='*.py', top_level_dir='../')

    success = nose.run(suite=suite)

    # Return process failure if tests fail.
    if not success:
        sys.exit(1)

    else:
        sys.exit(0)


if __name__ == '__main__':
    logging.disable(logging.CRITICAL)

    sdk_path = os.environ.get(
        'GAE_SDK_PATH',
        '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/'
    )

    main(sdk_path)
