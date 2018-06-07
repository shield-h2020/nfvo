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


from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import StringField

import datetime


class IsolationPolicy(Document):
    """
    SdnController (ODL) model
    """
    date = DateTimeField(default=datetime.datetime.now)
    name = StringField(required=True)
    meta = {"allow-inheritance": True, "abstract": True}


class InterfaceDown(IsolationPolicy):
    """
    Isolation policy (set down an interface)
    """
    interface_name = StringField(required=True)


class DeleteFlow(IsolationPolicy):
    """
    Isolation policy (delete flow from controller)
    """
    flow_id = StringField()
    rule = StringField()
