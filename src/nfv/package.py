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
from io import BytesIO
from mimetypes import MimeTypes
from nfvo.osm import endpoints as osm_eps
from pathlib import Path
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.package import MockPackage as package_m
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import ImmutableMultiDict

import json
import os
import re
import requests
import tarfile
import shutil
import yaml


class PackageFormatException(Exception):
    pass


class PackageNameException(Exception):
    pass


def post_content(bin_file):
    return
    data_file = ImmutableMultiDict([("package", bin_file)])
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    resp = requests.post(
            osm_eps.PKG_ONBOARD,
            headers=osm_eps.get_default_headers(),
            files=data_file,
            verify=False)
    output = json.loads(resp.text)
    output.update({"package": bin_file.filename})
    return output


def extract_type_and_version(filename):
    path = Path(filename)
    type_version = re.search("(vnfd|nsd)_(\d+\.\d+)",
                             path.name.strip(".tar.gz"))
    try:
        package_type = type_version.group(1)
        package_version = type_version.group(2)
    except AttributeError:
        raise PackageNameException
    return package_type, package_version


def process_package(bin_file, ptype, pversion):
    io_bytes = BytesIO(bin_file.read())
    tfiles = []
    try:
        tar = tarfile.open(mode="r:gz", fileobj=io_bytes)
        for member in tar.getnames():
            filename, extension = os.path.splitext(member)
            if extension != ".yaml":
                try:
                    tfiles.append(
                        {"tinfo": tarfile.TarInfo(member),
                         "buffer": tar.extractfile(member).read()})
                except AttributeError:
                    print("Skipping {0} (not readable)".format(member))
                continue
            descriptor = yaml.load(tar.extractfile(member).read())
            if "{0}:{0}-catalog".format(ptype) in descriptor:
                catalog = descriptor["{0}:{0}-catalog".format(ptype)]
                packs = catalog["{0}:{0}".format(ptype)]
                for pack in packs:
                    pack["{0}:version".format(ptype)] = pversion
            tfiles.append(
                {"tinfo": tarfile.TarInfo(member),
                 "buffer": bytearray(yaml.dump(descriptor), "utf-8")})
        tar.close()
        wo_bytes = BytesIO()
        wtar = tarfile.open(mode="w:gz", fileobj=wo_bytes)
        for tfile in tfiles:
            print("Adding {0} to tar".format(tfile["tinfo"]))
            wtar.addfile(tarinfo=tfile["tinfo"],
                         fileobj=BytesIO(tfile["buffer"]))
        wtar.close()
        wo_bytes.seek(0)
        return wo_bytes
    except tarfile.ReadError:
        raise PackageFormatException


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
        filename = pkg_path.filename
        ptype, pversion = extract_type_and_version(filename)
    else:
        if not os.path.isfile(pkg_path):
            remove_after = True
        if os.path.isfile(pkg_path):
            fp = open(pkg_path, "rb")
            filename = os.path.basename(pkg_path)
            ptype, pversion = extract_type_and_version(filename)
            mime = MimeTypes()
            content_type = mime.guess_type(pkg_path)
            bin_file = FileStorage(fp, filename, "package", content_type)
    bin_file = process_package(bin_file, ptype, pversion)
    # transform bin_file according type and version
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
