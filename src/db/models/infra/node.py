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


from db.models.auth.auth import Auth
from db.models.isolation.isolation_policy import IsolationPolicy
from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import StringField

import datetime


class Node(Document):
    """
    Node model
    """
    date = DateTimeField(default=datetime.datetime.now)
    host_name = StringField(required=True)
    ip_address = StringField(required=True)
    pcr0 = StringField(required=True)
    driver = StringField(required=True)
    analysis_type = StringField(required=True)
    distribution = StringField(required=True)
    isolated = BooleanField(default=False)
    terminated = BooleanField(default=False)
    authentication = ReferenceField(Auth, required=True)
    isolation_policy = ReferenceField(IsolationPolicy, required=True)
    termination_policy = ReferenceField(IsolationPolicy, required=True)
    disabled = BooleanField(required=True)
    physical = BooleanField(required=True)
    # Only needed in case node corresponds to VDUs
    instance_id = StringField(required=False)
    vnfr_id = StringField(required=False)
