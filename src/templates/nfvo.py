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


exec_action = """
{
    "input": {
               "name": "",
               "nsr_id_ref": "",
               "vnf-list": []
    }
}"""

exec_action_vnf = """
{
    "member_vnf_index_ref": "",
    "vnf-primitive": [
        {
            "name": "",
            "index": "",
            "parameter": [
                {
                    "name": "",
                    "value": ""
                }
            ]
        }
    ],
    "vnfr-id-ref": ""
}
"""

exec_action_encoded = """
name={name}&nsr_id_ref={ns_id}&vnf-list[0][member_vnf_index_ref]={vnf_index}&vnf-list[0][vnfr-id-ref]={vnf_id}&vnf-list[0][vnf-primitive][0][name]={action_name}&vnf-list[0][vnf-primitive][0][index]={action_idx}{action_data}&triggered-by=vnf-primitive
"""

exec_action_vnf_encoded = """
&vnf-list[0][vnf-primitive][0][parameter][{idx}][name]={param_name}&vnf-list[0][vnf-primitive][0][parameter][{idx}][value]={param_value}
"""
