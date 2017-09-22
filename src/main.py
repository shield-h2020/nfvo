#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server.http_server import Server

import sys


def main(argv=None):
    if not argv:
        argv = sys.argv
    try:
        Server().runServer()
    except KeyboardInterrupt:
        return True
    except Exception as e:
        sys.stderr.write("Got an exception: %s\n" % str(e))
        return False
    return True


if __name__ == '__main__':
    sys.exit(main())
