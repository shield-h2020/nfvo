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
from db.models.compute.compute_node import ComputeNode
from db.models.isolation.isolation_policy import IsolationPolicy
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import StringField

import datetime


class Vdu(Document):
    """
    Vdu model
    """
    date = DateTimeField(default=datetime.datetime.now)
    name = StringField(required=True)
    management_ip = StringField(required=True)
    authentication = ReferenceField(Auth, required=True)
    isolation_policy = ReferenceField(IsolationPolicy, required=True)
    compute_node = ReferenceField(ComputeNode, required=True)
