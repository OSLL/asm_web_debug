#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import sys

from basic_test import BasicTest
from open_pages_test import OpenPagesTest

DEFAULT_URL = "http://127.0.0.1:5000"

def main(host):
    suite = unittest.TestSuite()
    suite.addTest(BasicTest.parametrize(OpenPagesTest, param=host))

    returnCode = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    sys.exit(returnCode)


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) == 2 else DEFAULT_URL
    main(host)