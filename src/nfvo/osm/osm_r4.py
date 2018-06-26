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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_authorization(f):
    """
    Decorator to validate authorization prior API call
    """
    def wrapper(*args):
        response = requests.get(args[0].ns_descriptors_url,
                                headers=args[0].headers,
                                verify=False)
        if response.status_code == 401:
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
        config.read('conf/nfvo.conf')
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
        self.pnf_descriptors_url = "{0}/osm/nsd/v1/pnf_descriptors".\
                                   format(self.base_url)
        self.instantiate_url = "{0}/osm/nslcm/v1/ns_instances".\
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
        response = requests.post(self.instantiate_url,
                                 headers=self.headers,
                                 verify=False,
                                 json={"nsdId": nsd_id,
                                       "nsName": name,
                                       "nsDescription": description,
                                       "vimAccountId": vim_account_id})
        instantiation_data = json.loads(response.text)
        inst_url = "{0}/{1}/instantiate".format(self.instantiate_url,
                                                instantiation_data["id"])
        requests.post(inst_url,
                      headers=self.headers,
                      verify=False,
                      json={"nsFlavourId": flavor})
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
    def get_ns_instance(self, nsr_id=None):
        if nsr_id is not None:
            inst_url = "{0}/{1}".format(self.instantiate_url,
                                        nsr_id)
        else:
            inst_url = "{0}".format(self.instantiate_url)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

if __name__ == "__main__":
    OSM = OSMR4()
    NSD_IDS = [x["_id"] for x in OSM.get_ns_descriptors()]
    NSR = OSM.post_ns_instance(random.choice(NSD_IDS),
                               "Test",
                               "Test instance")
    print(OSM.get_ns_instance(NSR["id"]))
    time.sleep(5)
    OSM.delete_ns_instance(NSR["id"])
