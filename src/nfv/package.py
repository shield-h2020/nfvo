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
from nfvo.osm.osm_r4 import OSMR4
from nfvo.osm.osm_r4 import OSMException
from nfvo.osm.osm_r4 import OSMPackageConflict
from nfvo.osm.osm_r4 import OSMPackageError
from nfvo.osm.osm_r4 import OSMUnknownPackageType
from nfvo.osm.osm_r4 import OSMPackageNotFound
from server.http import content
from server.mocks.package import MockPackage as package_m


class NFVPackageConflict(Exception):
    pass


class NFVPackageError(Exception):
    pass


class NFVUnknownPackageType(Exception):
    pass


class NFVPackageNotFound(Exception):
    pass


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
    if release == 4:
        orchestrator = OSMR4()
    try:
        return orchestrator.onboard_package(pkg_path)
    except OSMPackageConflict:
        raise NFVPackageConflict
    except OSMUnknownPackageType:
        raise NFVUnknownPackageType
    except OSMPackageError:
        raise NFVPackageError


@content.on_mock(package_m().onboard_package_remote_mock)
def onboard_package_remote(pkg_path, release=None):
    """
    Uploads a remotely stored VNF or NS package to the NFVO.

    @param pkg_path Remote path to the package
    @return output Structure with provided path and transaction ID
    """
    orchestrator = OSMR2()
    if release == 4:
        orchestrator = OSMR4()
    return orchestrator.onboard_package_remote(pkg_path)


@content.on_mock(package_m().remove_package_mock)
def remove_package(pkg_name, release=None):
    orchestrator = OSMR2()
    if release == 4:
        orchestrator = OSMR4()
    try:
        return orchestrator.remove_package(pkg_name)
    except OSMUnknownPackageType:
        raise NFVUnknownPackageType
    except OSMPackageNotFound:
        raise NFVPackageNotFound
    except OSMPackageConflict:
        raise NFVPackageConflict
    except OSMException:
        raise OSMException
