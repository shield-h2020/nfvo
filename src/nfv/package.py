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


from nfvo.osm.osm_r2 import OSMR2
from server.http import content
from server.mocks.package import MockPackage as package_m


@content.on_mock(package_m().onboard_package_mock)
def onboard_package(pkg_path, release=None):
    """
    Uploads a locally stored VNF or NS package to the NFVO.
    Calling this method and POSTing a file from a remote server will
    result into more time to transfer the package.

    @param pkg_path Local binary file
    @return output Structure with provided path and transaction ID
    """
    orchestrator = OSMR2()
    return orchestrator.onboard_package(pkg_path)


@content.on_mock(package_m().onboard_package_remote_mock)
def onboard_package_remote(pkg_path, release=None):
    """
    Uploads a remotely stored VNF or NS package to the NFVO.

    @param pkg_path Remote path to the package
    @return output Structure with provided path and transaction ID
    """
    orchestrator = OSMR2()
    return orchestrator.onboard_package_remote(pkg_path)


@content.on_mock(package_m().remove_package_mock)
def remove_package(pkg_name, release=None):
    orchestrator = OSMR2()
    return orchestrator.remove_package(pkg_name)
