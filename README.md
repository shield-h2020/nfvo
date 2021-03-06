# vNSFO API

The vNSFO used in SHIELD consists of the [OSM MANO](https://osm.etsi.org) on one hand, and on a lightweight API that implements extra functionalities demanded by the project.

The orchestrator is a central element which covers the deployment of the Virtual Network Secure Functions (vNSF) provided by SHIELD and its lifecycle management. The API provides means to interact with other components of the SHIELD platform, e.g. pushing configurations in Medium Security Policy Language (MSPL) and exert them to specific vNSF.

# Installation

## Prerequisites

[Git](https://git-scm.com/) is required to download the source code. All other dependencies should be installed through the deployment script.
```
./bin/deploy.sh
```

## First set-up

If HTTPS and/or client certificate is enabled, PKI data must be generated first.
```
./bin/gen_creds.sh
```
Similarly, configuration data must be copied from the provided samples. This will fill with the proper IPs. **Note** that the vNSFO must run in the same host as OSM.
```
./bin/set_conf.sh
```

# Deployment

## Normal run

Directly execute the main script:
```
python3 src/main.py
```

## Docker way

First, log in as super user.

### Docker & Python3 dependencies

Tested on Ubuntu 16.04 with Docker 17.09.1-ce:

```
$ sudo apt-get install python3 python3-pip -y
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo apt-get update
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
$ sudo apt-get install docker-ce=17.09.1~ce-0~ubuntu
$ sudo usermod -G docker $(whoami)
$ sudo pip3 install docker-compose==1.17.1
```

### Deployment

Run the main script ./setup.sh:
```
./setup.sh
```

To tear down all related containers:
```
./teardown.sh
```

# API

## Documentation

The documentation follows the [OpenAPI Specification](https://swagger.io/specification/) (aka Swagger RESTful API Documentation Specification) version 2.0.
It is defined in the [endpoints.yaml](src/server/endpoints.yaml) file; and can be consulted in a user-friendly way by pointing your browser to the root of the vNSFO API server or directly paste the contents into [Swagger Editor](https://editor.swagger.io/).

## Usage

Refer to the samples below for easy testing of the REST methods. You can find the full reference in the OpenAPI definition.

**Important**: some methods are OSM-release specific. If no release is provided in the URL, it defaults to OSMr2.

### Common

#### List all API methods

```
curl -ik https://127.0.0.1:8448
```

### NS

#### Provide the available NSs

```
curl -ik https://127.0.0.1:8448/ns/config
```

#### Instantiate an already registered NS

VDU instances belonging to a NS are registered as infrastructure nodes via the vNSFO.
Extra configuration (NFVI optional fields) can be included inside the instantiation body:

- analysis_type (string)
- pcr0 (string)
- driver (string)
- distribution (string)
- authentication (see NFVI section for samples)
- isolation_policy (see NFVI section for samples)
- termination_policy (see NFVI section for samples)

Since these are optional, if not provided in the request, default values will be used.

Incompatibility of parameters:
- "attack_type" and {"ns_name", "instance_name"} cannot be used at the same type. Attack type has precedence if some of the others is used.

##### Specific deployment location and provider network

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "vim_id": "f9acd550-9d48-11e7-ae4c-00163e3afbe5", "vim_net": "provider"}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "vim_id": "f9acd550-9d48-11e7-ae4c-00163e3afbe5", "vim_net": "provider"}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "vim_id": "f9acd550-9d48-11e7-ae4c-00163e3afbe5", "vim_net": "provider"}'
```

##### Random deployment location and provider network

###### Specific NS and given name for instance

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd"}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd"}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd"}'
```

###### Per type of attack (NS and instance name taken from internal mapping)

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"attack_type": "dos"}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"attack_type": "slowloris"}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"attack_type": "TCP flood"}'
```

##### Using a vim supporting Docker

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "virt_type": "docker"}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "virt_type": "docker"}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "virt_type": "docker"}'
```

##### Deploy explicitly using a kvm vim (default behavior)

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "virt_type": "kvm"}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "virt_type": "kvm"}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "virt_type": "kvm"}'
```

##### Instantiate and perform VNSF action asynchronously

###### Waiting for NS default target status

Default target status (target_status) is defined in conf/nfvo.mspl.conf.sample

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}}'
```

###### Waiting for NS custom target_status

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}, "target_status": "active"}'

curl -ik https://127.0.0.1:8448/ns/r2/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}, "target_status": "active"}'

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}, "target_status": "active"}'
```

#### Delete an already instantiated NS

```
# OSM release TWO (default and explicit modes)
curl -ik -X DELETE https://127.0.0.1:8448/ns/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259

curl -ik -X DELETE https://127.0.0.1:8448/ns/r2/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259

# OSM release FOUR
curl -ik -X DELETE https://127.0.0.1:8448/ns/r4/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259
```

#### Provide the running NSs

##### All NSs

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/ns/running

curl -ik https://127.0.0.1:8448/ns/r2/running

# OSM release FOUR
curl -ik https://127.0.0.1:8448/ns/r4/running
```

##### Specific NS instance

```
# OSM release TWO (default and explicit modes)

# Option A1: using NSR ID
curl -ik https://127.0.0.1:8448/ns/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259
# Option A2: using name of the NS instance
curl -ik https://127.0.0.1:8448/ns/running/fl7f_test

# Option B1: using NSR ID
curl -ik https://127.0.0.1:8448/ns/r2/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259
# Option B2: using name of the NS instance
curl -ik https://127.0.0.1:8448/ns/r2/running/fl7f_test

# OSM release FOUR

# Option C1: using NSR ID
curl -ik https://127.0.0.1:8448/ns/r4/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259
# Option C2: using name of the NS instance
curl -ik https://127.0.0.1:8448/ns/r4/running/fl7f_test
```

### Package

#### Onboard a locally stored package into NFVO

```
# OSM release TWO (default and explicit modes)

curl -ik https://127.0.0.1:8448/package/onboard -X POST \
     -H "Content-Type: multipart/form-data" \
     -F "package=@/tmp/cirros_vnf.tar.gz"

curl -ik https://127.0.0.1:8448/package/r2/onboard -X POST \
     -H "Content-Type: multipart/form-data" \
     -F "package=@/tmp/cirros_vnf.tar.gz"

# OSM release FOUR

curl -ik https://127.0.0.1:8448/package/r4/onboard -X POST \
     -H "Content-Type: multipart/form-data" \
     -F "package=@/tmp/cirros_vnf.tar.gz"
```

#### Onboard a remotely stored package into NFVO

```
# OSM release TWO (default and explicit modes)

curl -ik https://127.0.0.1:8448/package/onboard/remote -X POST \
     -H "Content-Type: application/json" \
     -d '{"path": "https://osm-download.etsi.org/ftp/examples/cirros_2vnf_ns/cirros_vnf.tar.gz"}'

curl -ik https://127.0.0.1:8448/package/r2/onboard/remote -X POST \
     -H "Content-Type: application/json" \
     -d '{"path": "https://osm-download.etsi.org/ftp/examples/cirros_2vnf_ns/cirros_vnf.tar.gz"}'

# OSM release FOUR

curl -ik https://127.0.0.1:8448/package/r4/onboard/remote -X POST \
     -H "Content-Type: application/json" \
     -d '{"path": "https://osm-download.etsi.org/ftp/examples/cirros_2vnf_ns/cirros_vnf.tar.gz"}'
```

#### Remove package from vNSFO

```
curl -ik https://127.0.0.1:8448/package/cirros_vnfd -X DELETE
```

### VIM

#### Provide the list of registered VIMs

```
curl -ik https://127.0.0.1:8448/vim
```

#### Provide the list of available VDU

```
curl -ik https://127.0.0.1:8448/vim/image
```

#### Register a locally stored VDU image into a specific VIM

```
vim_id="356fc757-c0c1-4b9e-b0db-d5cb46edd658"
curl -ik https://127.0.0.1:8448/vim/image/${vim_id} -X POST \
     -H "Content-Type: multipart/form-data" \
     -F "image=@/tmp/Fedora-x86_64-20-20131211.1-sda-ping.qcow2"
```

### vNSF

#### Provide the available vNSFs

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/vnsf/config

curl -ik https://127.0.0.1:8448/vnsf/r2/config

# OSM release FOUR
curl -ik https://127.0.0.1:8448/vnsf/r4/config
```

#### Provide the running vNSFs

```
# OSM release TWO (default and explicit modes)
curl -ik https://127.0.0.1:8448/vnsf/running

curl -ik https://127.0.0.1:8448/vnsf/r2/running

# OSM release FOUR
curl -ik https://127.0.0.1:8448/vnsf/r4/running
```

#### Execute pre-defined action from a specific vNSF

```
# OSM release TWO (default and explicit modes)
curl -ki https://127.0.0.1:8448/vnsf/action -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "vnsf_id": "2145d576-1b91-4cb1-9b76-77f2aeab21cd", "action": "set-policies", "params": { "policies": "<mspl-set xmlns=\"http://security.polito.it/shield/mspl\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://security.polito.it/shield/mspl mspl.xsd\"><it-resource id=\"2145d576-1b91-4cb1-9b76-77f2aeab21cd\"><configuration xsi:type=\"filtering-configuration\"><default-action>drop</default-action><resolution-strategy>FMR</resolution-strategy><rule><priority>101</priority><action>drop</action><condition><packet-filter-condition><direction>inbound</direction><direction>inbound</direction><source-address>10.30.0.190</source-address><protocol>UDP</protocol></packet-filter-condition><traffic-flow-condition><rate-limit>36kbit</rate-limit></traffic-flow-condition></condition></rule></configuration></it-resource></mspl-set>" } }'

curl -ki https://127.0.0.1:8448/vnsf/r2/action -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "vnsf_id": "2145d576-1b91-4cb1-9b76-77f2aeab21cd", "action": "set-policies", "params": { "policies": "<mspl-set xmlns=\"http://security.polito.it/shield/mspl\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://security.polito.it/shield/mspl mspl.xsd\"><it-resource id=\"2145d576-1b91-4cb1-9b76-77f2aeab21cd\"><configuration xsi:type=\"filtering-configuration\"><default-action>drop</default-action><resolution-strategy>FMR</resolution-strategy><rule><priority>101</priority><action>drop</action><condition><packet-filter-condition><direction>inbound</direction><direction>inbound</direction><source-address>10.30.0.190</source-address><protocol>UDP</protocol></packet-filter-condition><traffic-flow-condition><rate-limit>36kbit</rate-limit></traffic-flow-condition></condition></rule></configuration></it-resource></mspl-set>" } }'

# OSM release FOUR
curl -ki https://127.0.0.1:8448/vnsf/r4/action -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "vnsf_id": "2145d576-1b91-4cb1-9b76-77f2aeab21cd", "action": "set-policies", "params": { "policies": "<mspl-set xmlns=\"http://security.polito.it/shield/mspl\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://security.polito.it/shield/mspl mspl.xsd\"><it-resource id=\"2145d576-1b91-4cb1-9b76-77f2aeab21cd\"><configuration xsi:type=\"filtering-configuration\"><default-action>drop</default-action><resolution-strategy>FMR</resolution-strategy><rule><priority>101</priority><action>drop</action><condition><packet-filter-condition><direction>inbound</direction><direction>inbound</direction><source-address>10.30.0.190</source-address><protocol>UDP</protocol></packet-filter-condition><traffic-flow-condition><rate-limit>36kbit</rate-limit></traffic-flow-condition></condition></rule></configuration></it-resource></mspl-set>" } }'
```

### NFVI

#### Register a new node using private key and delete flow as isolation policy

```
curl -ki https://127.0.0.1:8448/nfvi/node -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "host_name": "node.test", "ip_address": "192.168.10.2", "pcr0": "??", "driver": "OAT", "analysis_type": "FULL", "distribution": "xenial", "authentication": { "username": "user", "type": "private_key", "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEqAIBAAKCAQEAnaSdeeE/bcAxgsivLliDhRE017ZK74m2QYg58QNbfdzoNba2 ..." }, "isolation_policy": { "name": "delflow", "type": "delflow", "flow_id": "21", "rule": "rule1" } }'
```

#### Register a new node using password and interface down isolation policy

```
curl -ki https://127.0.0.1:8448/nfvi/node -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "host_name": "node.test", "ip_address": "192.168.10.2", "pcr0": "??", "driver": "OAT", "analysis_type": "FULL", "distribution": "xenial", "authentication": { "username": "user", "type": "password", "password": "password" }, "isolation_policy": { "name": "Eth0Down", "type": "ifdown", "interface_name": "eth0" } }'
```

#### Register a new node using password, ifdown isolation policy and shutdown termination policy

```
curl -ki https://127.0.0.1:8448/nfvi/node -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "host_name": "node.test", "ip_address": "192.168.10.2", "pcr0": "??", "driver": "OAT", "analysis_type": "FULL", "distribution": "xenial", "authentication": { "username": "user", "type": "password", "password": "password" }, "isolation_policy": { "name": "ifdown", "type": "ifdown", "interface_name": "ens2f0" }, "termination_policy": { "name": "shutdown", "type": "shutdown", "command": "sudo poweroff" } }'
```

#### Deregister a node and associated data

```
curl -ki https://127.0.0.1:8448/nfvi/node/5b2908871745ba000163bf9e -X DELETE
```

#### Isolate a node

```
# Option 1: using {"isolated": true} as body in a PUT request
curl -ki https://127.0.0.1:8448/nfvi/node/5b2908871745ba000163bf9e -X PUT \
     -H 'Content-Type: application/json' \
     -d '{ "isolated": true }'
# Option 2: isolate POST endpoint
curl -ki https://127.0.0.1:8448/nfvi/node/5b2908871745ba000163bf9e/isolate -X POST \
     -H 'Content-Type: application/json'
```

#### Terminate a node

```
# Option 1: using {"terminated": true} as body in a PUT request
curl -ki https://127.0.0.1:8448/nfvi/node/5b2908871745ba000163bf9e -X PUT \
     -H 'Content-Type: application/json' \
     -d '{ "terminated": true }'
# Option 2: terminate POST endpoint
curl -ki https://127.0.0.1:8448/nfvi/node/5b2908871745ba000163bf9e/terminate -X POST \
     -H 'Content-Type: application/json'
```

#### Get information and isolation status for all or specific nodes

```
curl -ki https://127.0.0.1:8448/nfvi/node
curl -ki https://127.0.0.1:8448/nfvi/node/5b2908871745ba000163bf9e
curl -ki https://127.0.0.1:8448/nfvi/node/physical
curl -ki https://127.0.0.1:8448/nfvi/node/physical/isolated
curl -ki https://127.0.0.1:8448/nfvi/node/physical/trusted
curl -ki https://127.0.0.1:8448/nfvi/node/virtual
curl -ki https://127.0.0.1:8448/nfvi/node/virtual/isolated
curl -ki https://127.0.0.1:8448/nfvi/node/virtual/trusted
```

#### Get SDN flows from the internal reference

```
curl -ik https://84.88.40.183:8448/nfvi/network/reference/flows
```

#### Get SDN flows from the internal database

```
# All flows
curl -ik https://127.0.0.1:8448/nfvi/network/config/flows
# Specific flow
curl -ik https://127.0.0.1:8448/nfvi/network/config/flows/L2switch-0
```

#### Get SDN flows from the switch

```
# All flows
curl -ik https://127.0.0.1:8448/nfvi/network/running/flows
# Specific flow
curl -ik https://127.0.0.1:8448/nfvi/network/running/flows/L2switch-0
```

#### Push SDN flows to switch

```
curl -ik -H "Accept:application/xml" -H "Content-Type:application/xml" -X POST https://127.0.0.1:8448/nfvi/network/running/flows/L2switch-0 --data '<flow xmlns="urn:opendaylight:flow:inventory"><id>L2switch-0</id><hard-timeout>0</hard-timeout><idle-timeout>0</idle-timeout><cookie>3098476543630901248</cookie><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><max-length>65535</max-length><output-node-connector>NORMAL</output-node-connector></output-action></action></apply-actions></instruction></instructions><priority>101</priority><flow-statistics xmlns="urn:opendaylight:flow:statistics"><packet-count>0</packet-count><byte-count>0</byte-count><duration><nanosecond>42000000</nanosecond><second>2064</second></duration></flow-statistics><table_id>0</table_id></flow>'
```

#### Delete SDN flow from switch

```
# All flows
curl -ik -X DELETE https://127.0.0.1:8448/nfvi/network/config/flows
# Specific flow
curl -ik -X DELETE https://127.0.0.1:8448/nfvi/network/config/flows/L2switch-0
```

# Testing

Run all tests, or either mocked or real-time/live tests.

## All tests

```
./setup.sh --test
```

## Mocked tests

```
./setup.sh --test-mocked
```

## Real time tests

```
./setup.sh --test-realtime
```
