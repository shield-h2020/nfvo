#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys

from server.http.server import Server


def main():
    try:
        Server().run()
    except KeyboardInterrupt:
        return True
    except Exception as e:
        sys.stderr.write("Exception running server: {}\n".format(e))
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
