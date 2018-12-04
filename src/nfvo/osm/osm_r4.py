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

import configparser
import json
import random
import requests
import time
import urllib3

from core.log import setup_custom_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGGER = setup_custom_logger(__name__)


def check_authorization(f):
    """
    Decorator to validate authorization prior API call
    """
    def wrapper(*args):
        response = requests.get(args[0].ns_descriptors_url,
                                headers=args[0].headers,
                                verify=False)
        if response.status_code in (401, 500):
            args[0].new_token(args[0].username,
                              args[0].password)
        return f(*args)
    return wrapper


class OSMR4():
    """
    OSM release 4 northbound API client (NBI)
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../conf/nfvo.conf')
        self.base_url = "{0}://{1}:{2}".format(
            config["nbi"]["protocol"],
            config["nbi"]["host"],
            config["nbi"]["port"])
        self.default_dc = config["nbi"]["default_om_datacenter"]
        self.default_flavor = config["nbi"]["default_flavor"]
        self.token_url = "{0}/osm/admin/v1/tokens".format(self.base_url)
        self.ns_descriptors_url = "{0}/osm/nsd/v1/ns_descriptors".\
                                  format(self.base_url)
        self.ns_descriptors_content_url = \
            "{0}/osm/nsd/v1/ns_descriptors_content".\
            format(self.base_url)
        self.vnf_descriptors_url = "{0}/osm/vnfpkgm/v1/vnf_packages".\
                                   format(self.base_url)
        self.vnf_instances_url = "{0}/osm/nslcm/v1/vnfrs".\
                                 format(self.base_url)
        self.instantiate_url = "{0}/osm/nslcm/v1/ns_instances".\
                               format(self.base_url)
        self.vim_accounts_url = "{0}/osm/admin/v1/vim_accounts".\
                                format(self.base_url)
        self.headers = {"Accept": "application/json"}
        self.token = None
        self.username = config["nbi"]["username"]
        self.password = config["nbi"]["password"]

    def new_token(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        response = requests.post(self.token_url,
                                 json={"username": self.username,
                                       "password": self.password},
                                 headers=self.headers,
                                 verify=False)
        token = json.loads(response.text).get("id")
        self.headers.update({"Authorization": "Bearer {0}".format(token)})
        return token

    @check_authorization
    def get_ns_descriptors(self):
        response = requests.get(self.ns_descriptors_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    @check_authorization
    def get_ns_descriptors_content(self):
        response = requests.get(self.ns_descriptors_content_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    @check_authorization
    def get_pnf_descriptors(self):
        response = requests.get(self.pnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    @check_authorization
    def post_ns_instance(self, nsd_id, name, description,
                         vim_account_id=None, flavor=None):
        if vim_account_id is None:
            vim_account_id = self.default_dc
        if flavor is None:
            flavor = self.default_flavor
        ns_data = {"nsdId": nsd_id,
                   "nsName": name,
                   "nsDescription": description,
                   "vimAccountId": vim_account_id,
                   "flavourId": flavor}
        response = requests.post(self.instantiate_url,
                                 headers=self.headers,
                                 verify=False,
                                 json=ns_data)
        instantiation_data = json.loads(response.text)
        inst_url = "{0}/{1}/instantiate".format(self.instantiate_url,
                                                instantiation_data["id"])
        requests.post(inst_url,
                      headers=self.headers,
                      verify=False,
                      json=ns_data)
        return instantiation_data

    @check_authorization
    def delete_ns_instance(self, nsr_id):
        inst_url = "{0}/{1}".format(self.instantiate_url,
                                    nsr_id)
        requests.post("{0}/terminate".format(inst_url),
                      headers=self.headers,
                      verify=False)
        requests.delete(inst_url,
                        headers=self.headers,
                        verify=False)

    @check_authorization
    def get_ns_instances(self, nsr_id=None):
        if nsr_id is not None:
            inst_url = "{0}/{1}".format(self.instantiate_url,
                                        nsr_id)
        else:
            inst_url = "{0}".format(self.instantiate_url)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        ns_instances = json.loads(response.text)
        ns_data = {"ns":
                   [self.translate_ns_instance(x) for x in ns_instances]}
        return ns_data

    def translate_ns_instance(self, nsi):
        tnsi = {}
        tnsi["config_status"] = nsi["config-status"]
        tnsi["constituent_vnf_instances"] = []
        for vnfi in self.get_vnf_instances(nsi["_id"]):
            vnfi.update({"ns_name": nsi.get("ns_name", nsi.get("name"))})
            vnfi.update({"vnfr_name": "{0}__{1}__1".format(nsi["nsd-name-ref"],
                                                           vnfi["vnfd_id"])})
            tnsi["constituent_vnf_instances"].append(vnfi)
        tnsi["instance_id"] = nsi["id"]
        tnsi["name"] = nsi["name"]
        tnsi["ns_name"] = nsi["nsd-name-ref"]
        tnsi["nsd_id"] = nsi["nsd-ref"]
        tnsi["operational_status"] = nsi["operational-status"]
        if tnsi["operational_status"] == "ACTIVE":
            tnsi["operational_status"] = "running"
        tnsi["vlrs"] = []
        return tnsi

    @check_authorization
    def get_vnf_instances(self, ns_instance_id):
        url = "{0}?nsr-id-ref={1}".format(
            self.vnf_instances_url, ns_instance_id)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vnfis = json.loads(response.text)
        return [self.translate_vnf_instance(x) for x in vnfis]

    def translate_vnf_instance(self, vnfi):
        tvnfi = {}
        vdur = {}
        if len(vnfi["vdur"]) > 0:
            vdur = vnfi["vdur"][0]
        tvnfi["operational_status"] = vdur.get("status", None)
        tvnfi["config_jobs"] = []
        if tvnfi["operational_status"] == "ACTIVE":
            tvnfi["operational_status"] = "running"
        tvnfi["config_status"] = "config-not-needed"
        tvnfi["ip"] = vdur.get("ip-address", None)
        tvnfi["ns_id"] = vnfi.get("nsr-id-ref")
        vnfd = self.get_vnf_descriptor(vnfi.get("vnfd-ref", None))
        if vnfd:
            tvnfi["vendor"] = vnfd["vendor"]
        else:
            tvnfi["vendor"] = None
        vim = self.get_vim_account(vnfi.get("vim-account-id"))
        if vim:
            tvnfi["vim"] = vim["name"]
        else:
            tvnfi["vim"] = None
        tvnfi["vnfd_id"] = vnfi["vnfd-ref"]
        tvnfi["vnfr_id"] = vnfi["id"]
        return tvnfi

    def get_vnf_descriptor(self, vnf_name):
        url = "{0}?name={1}".format(
            self.vnf_descriptors_url, vnf_name)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vnfds = json.loads(response.text)
        target_vnfd = None
        for vnfd in vnfds:
            if vnfd["name"] == vnf_name:
                target_vnfd = vnfd
        return target_vnfd

    def get_vim_account(self, vim_account_id):
        url = "{0}".format(self.vim_accounts_url)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vims = json.loads(response.text)
        target_vim = None
        for vim in vims:
            if str(vim["_id"]) == str(vim_account_id):
                target_vim = vim
        return target_vim


if __name__ == "__main__":
    OSM = OSMR4()
    NSD_IDS = [x["_id"] for x in OSM.get_ns_descriptors()]
    print(random.choice(NSD_IDS))
    NSR = OSM.post_ns_instance("833bb02c-92e4-4fdb-ac55-cc927acfd2e7",
                               "Test",
                               "Test instance")
    print(OSM.get_ns_instance(NSR["id"]))
    time.sleep(180)
    OSM.delete_ns_instance(NSR["id"])
