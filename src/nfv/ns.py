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

from core.config import FullConfParser
from core.log import setup_custom_logger
from flask import current_app
from nfvo.osm.osm_r2 import OSMR2
from nfvo.osm.osm_r4 import OSMR4
from server.http import content
from server.mocks.ns import MockNs as ns_m

import threading
import time


LOGGER = setup_custom_logger(__name__)


class VnsfoNs:

    def __init__(self, release=None):
        self.orchestrator = OSMR2()
        self.config = FullConfParser()
        self.nfvo_mspl_category = self.config.get("nfvo.mspl.conf")
        self.mspl_monitoring = self.nfvo_mspl_category.get("monitoring")
        self.monitoring_timeout = int(self.mspl_monitoring.get("timeout"))
        self.monitoring_interval = int(self.mspl_monitoring.get("interval"))
        self.monitoring_target_status = self.\
            mspl_monitoring.get("target_status")
        self.isolation_config = FullConfParser()
        self.isolation_category = self.config.get("isolation.conf")
        self.keys = self.isolation_category.get("keys")
        self.default_username = self.keys.get("default_username")
        self.default_key = self.keys.get("default_key")
        if release == 4:
            self.orchestrator = OSMR4()

    @content.on_mock(ns_m().get_nsr_config_mock)
    def get_nsr_config(self, ns_name=None):
        return self.orchestrator.get_ns_descriptors(ns_name)

    @content.on_mock(ns_m().get_nsr_running_mock)
    def get_nsr_running(self, instance_id=None):
        return self.orchestrator.get_ns_instances(instance_id)

    def monitor_deployment(self, instantiation_data, app, target_status=None):
        LOGGER.info("Monitoring deployment of instance: {0}".format(
            instantiation_data["instance_id"]))
        timeout = self.monitoring_timeout
        vdus_registered = False
        if target_status is None:
            target_status = self.monitoring_target_status
        while not vdus_registered:
            time.sleep(self.monitoring_interval)
            nss = self.orchestrator.get_ns_instances(
                instantiation_data["instance_id"])
            if timeout < 0:
                LOGGER.info("Timeout reached, aborting")
            if len(nss["ns"]) < 1:
                LOGGER.info("No instance found, aborting thread")
                break
            operational_status = nss["ns"][0].get("operational_status", "")
            if operational_status == "failed":
                LOGGER.info("Instance failed, aborting")
                break
            if operational_status == target_status and \
               "constituent_vnf_instances" in nss["ns"][0]:
                LOGGER.info("Network Service Deployed")
                LOGGER.info("Constituent VNF Instance data")
                if len(nss["ns"]) == 0:
                    # No VDUs, returning
                    return
                for vnfr in nss["ns"][0]["constituent_vnf_instances"]:
                    vnfr_name = vnfr["vnfr_name"]
                    vdu_ip = vnfr["ip"]
                with open(self.default_key) as fhandle:
                    key = fhandle.read()
                app.mongo.store_vdu(vnfr_name, vdu_ip,
                                    "sudo poweroff",
                                    self.default_username,
                                    key)
                break
            timeout -= self.monitoring_interval

    @content.on_mock(ns_m().post_nsr_instantiate_mock)
    def instantiate_ns(self, instantiation_data):
        instantiation_data = self.orchestrator.post_ns_instance(
            instantiation_data)
        t = threading.Thread(target=self.monitor_deployment,
                             args=(instantiation_data,
                                   current_app._get_current_object(),
                                   self.monitoring_target_status))
        t.start()
        return instantiation_data

    @content.on_mock(ns_m().delete_nsr_mock)
    def delete_ns(self, instance_id):
        return self.orchestrator.delete_ns_instance(instance_id)

    def fetch_config_nss(self):
        catalog = self.get_nsr_config()
        return catalog
