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


from core import download
from mimetypes import MimeTypes
from nfvo.osm import endpoints as osm_eps
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.package import MockPackage as package_m
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import ImmutableMultiDict

import json
import os
import requests
import shutil
import threading
import time


class PackageStatusException(Exception):
    pass


def get_package_status(transaction_id):
    url = "{0}/{1}/state?api_server=https://localhost".\
                                     format(osm_eps.PKG_STATUS,
                                            transaction_id)
    response = requests.get(url,
                            headers=osm_eps.get_default_headers(),
                            verify=False)
    try:
        return(json.loads(response.text))
    except json.decoder.JSONDecodeError:
        raise PackageStatusException


def track_status(transaction_id):
    status = ""
    counter = 3600
    while status not in ['success', 'failure'] and counter > 0:
        counter = counter - 1
        response = get_package_status(transaction_id)
        print(
            "Tracking PKG onboarding: {0}".format(response))
        status = response["status"]
        time.sleep(1)


def post_content(bin_file):
    data_file = ImmutableMultiDict([("package", bin_file)])
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    resp = requests.post(
            osm_eps.PKG_ONBOARD,
            headers=osm_eps.get_default_headers(),
            files=data_file,
            verify=False)
    transaction_id = json.loads(resp.text)["transaction_id"]
    track_thread = threading.Thread(target=track_status,
                                    args=(transaction_id,))
    track_thread.start()
    output = json.loads(resp.text)
    output.update({"package": bin_file.filename})
    return output


@content.on_mock(package_m().onboard_package_mock)
def onboard_package(pkg_path):
    """
    Uploads a locally stored VNF or NS package to the NFVO.
    Calling this method and POSTing a file from a remote server will
    result into more time to transfer the package.

    @param pkg_path Local binary file
    @return output Structure with provided path and transaction ID
    """
    remove_after = False

    fp = None
    bin_file = None
    output = None
    if type(pkg_path) == FileStorage:
        bin_file = pkg_path
    else:
        if not os.path.isfile(pkg_path):
            remove_after = True
        if os.path.isfile(pkg_path):
            fp = open(pkg_path, "rb")
            filename = os.path.basename(pkg_path)
            mime = MimeTypes()
            content_type = mime.guess_type(pkg_path)
            bin_file = FileStorage(fp, filename, "package", content_type)
    if bin_file is not None:
        output = post_content(bin_file)
    if fp is not None:
        fp.close()
    if remove_after:
        pkg_dir = os.path.dirname(pkg_path)
        shutil.rmtree(pkg_dir)
    return output


@content.on_mock(package_m().onboard_package_remote_mock)
def onboard_package_remote(pkg_path):
    """
    Uploads a remotely stored VNF or NS package to the NFVO.

    @param pkg_path Remote path to the package
    @return output Structure with provided path and transaction ID
    """
    if not os.path.isfile(pkg_path):
        pkg_path = download.fetch_content(pkg_path)
    return onboard_package(pkg_path)


@content.on_mock(package_m().remove_package_mock)
def remove_package(pkg_name):
    remove_url = osm_eps.PKG_VNF_REMOVE
    if "_ns" in pkg_name:
        remove_url = osm_eps.PKG_NS_REMOVE
    remove_url = remove_url.format(pkg_name)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    resp = requests.delete(
            remove_url,
            headers=osm_eps.get_default_headers(),
            verify=False)
    output = json.loads(resp.text)
    output.update({"package": pkg_name})
    return output
