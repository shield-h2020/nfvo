#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

#exec_action_encoded = """
#name={}&nsr_id_ref={}&vnf-list[0][member_vnf_index_ref]={}&vnf-list[0][vnfr-id-ref]={}&vnf-list[0][vnf-primitive][0][name]={}&vnf-list[0][vnf-primitive][0][index]={}&vnf-list[0][vnf-primitive][0][parameter][0][name]={}&vnf-list[0][vnf-primitive][0][parameter][0][value]={}&triggered-by=vnf-primitive
#"""

exec_action_encoded = """
name={name}&nsr_id_ref={ns_id}&vnf-list[0][member_vnf_index_ref]={vnf_index}&vnf-list[0][vnfr-id-ref]={vnf_id}&vnf-list[0][vnf-primitive][0][name]={action_name}&vnf-list[0][vnf-primitive][0][index]={action_idx}{action_data}&triggered-by=vnf-primitive
"""

exec_action_vnf_encoded = """
&vnf-list[0][vnf-primitive][0][parameter][{idx}][name]={param_name}&vnf-list[0][vnf-primitive][0][parameter][{idx}][value]={param_value}
"""
