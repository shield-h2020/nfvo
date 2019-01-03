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
from db.models.infra.node import Node
from flask import current_app
from nfvo.osm.osm_r2 import OSMR2
from nfvo.osm.osm_r4 import OSMR4
from server.http import content
from server.mocks.ns import MockNs as ns_m
from tm.tm_client import TMClient

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
        self.tm_config = FullConfParser()
        self.tm_category = self.tm_config.get("tm.conf")
        self.tm_general = self.tm_category.get("general")
        self.default_analysis_type = \
            self.tm_general.get("default_analysis_type")
        self.default_pcr0 = \
            self.tm_general.get("default_pcr0")
        self.default_distribution = \
            self.tm_general.get("default_distribution")
        self.default_driver = \
            self.tm_general.get("default_driver")
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
                if "authentication" not in instantiation_data:
                    with open(self.default_key) as fhandle:
                        key = fhandle.read()
                    instantiation_data["authentication"] = {
                        "private_key": key,
                        "type": "private_key",
                        "username": self.default_username
                    }
                if "isolation_policy" not in instantiation_data:
                    instantiation_data["isolation_policy"] = {
                        "command": "sudo poweroff",
                        "name": "shutdown",
                        "type": "shutdown"
                    }
                if "termination_policy" not in instantiation_data:
                    instantiation_data["termination_policy"] = {
                        "command": "sudo poweroff",
                        "name": "shutdown",
                        "type": "shutdown"
                    }
                app.mongo.store_vdu(vnfr_name, vdu_ip,
                                    instantiation_data["isolation_policy"],
                                    instantiation_data["termination_policy"],
                                    instantiation_data["authentication"],
                                    instantiation_data["analysis_type"],
                                    instantiation_data["pcr0"],
                                    instantiation_data["distribution"],
                                    instantiation_data["driver"],
                                    instantiation_data["instance_id"])
                node_data = {
                    "host_name": vnfr_name,
                    "ip_address": vdu_ip,
                    "distribution": instantiation_data["distribution"],
                    "pcr0": instantiation_data["pcr0"],
                    "driver": instantiation_data["driver"]}
                trust_monitor_client = TMClient()
                trust_monitor_client.register_node(node_data)
                break
            timeout -= self.monitoring_interval

    @content.on_mock(ns_m().post_nsr_instantiate_mock)
    def instantiate_ns(self, instantiation_data):
        nsi_data = self.orchestrator.post_ns_instance(
            instantiation_data)
        if "authentication" in instantiation_data:
            nsi_data["authentication"] = \
                instantiation_data["authentication"]
        if "isolation_policy" in instantiation_data:
            nsi_data["isolation_policy"] = \
                instantiation_data["isolation_policy"]
        if "termination_policy" in instantiation_data:
            nsi_data["termination_policy"] = \
                instantiation_data["termination_policy"]
        nsi_data["analysis_type"] = \
            self.default_analysis_type
        if "analysis_type" in instantiation_data:
            nsi_data["analysis_type"] = \
                instantiation_data["analysis_type"]
        nsi_data["pcr0"] = \
            self.default_pcr0
        if "pcr0" in instantiation_data:
            nsi_data["pcr0"] = \
                instantiation_data["pcr0"]
        nsi_data["distribution"] = \
            self.default_distribution
        if "distribution" in instantiation_data:
            nsi_data["distribution"] = \
                instantiation_data["distribution"]
        nsi_data["driver"] = \
            self.default_driver
        if "driver" in instantiation_data:
            nsi_data["driver"] = \
                instantiation_data["driver"]
        t = threading.Thread(target=self.monitor_deployment,
                             args=(nsi_data,
                                   current_app._get_current_object(),
                                   self.monitoring_target_status))
        t.start()
        return nsi_data

    @content.on_mock(ns_m().delete_nsr_mock)
    def delete_ns(self, instance_id):
        nodes = Node.objects(instance_id=instance_id)
        tm_client = TMClient()
        for node in nodes:
            LOGGER.info(node.host_name)
            tm_client.delete_node(node.host_name)
            node.delete()
        return self.orchestrator.delete_ns_instance(instance_id)

    def fetch_config_nss(self):
        catalog = self.get_nsr_config()
        return catalog
