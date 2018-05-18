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

Deploy and run tests:
```
./setup.sh --test
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

##### Specific deployment location and provider network

```
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd", "vim_id": "f9acd550-9d48-11e7-ae4c-00163e3afbe5", "vim_net": "provider"}'
```

##### Random deployment location and provider network

```
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "l3f_test", "ns_name": "l3filter_nsd"}'
```

##### Instantiate and perform VNSF action asynchronously

###### Waiting for NS default target status

Default target status (target_status) is defined in conf/nfvo.mspl.conf.sample

```
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}}'
```

###### Waiting for NS custom target_status

```
curl -ik https://127.0.0.1:8448/ns/instantiate -X POST \
     -H "Content-Type: application/json" \
     -d '{"instance_name": "fl7filter_test", "ns_name": "fl7filter_nsd", "action": "set-policies", "params": {"policies": "test-policy"}, "target_status": "active"}'
```

#### Delete an already instantiated NS

```
curl -ik -X DELETE https://127.0.0.1:8448/ns/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259
```

#### Provide the running NSs

##### All NSs

```
curl -ik https://127.0.0.1:8448/ns/running
```

##### Specific NS instance

```
# Option 1: using NSR ID
curl -ik https://127.0.0.1:8448/ns/running/c3fea13a-cc52-4bf9-bf12-3ed20bfb8259
# Option 2: using name of the NS instance
curl -ik https://127.0.0.1:8448/ns/running/fl7f_test
```

### Package

#### Onboards a locally stored package into NFVO

```
curl -ik https://127.0.0.1:8448/package/onboard -X POST \
     -H "Content-Type: multipart/form-data" \
     -F "package=@/tmp/cirros_vnf.tar.gz"
```

#### Onboards a remotely stored package into NFVO

```
curl -ik https://127.0.0.1:8448/package/onboard/remote -X POST \
     -H "Content-Type: application/json" \
     -d '{"path": "https://osm-download.etsi.org/ftp/examples/cirros_2vnf_ns/cirros_vnf.tar.gz"}'
```

#### Remove package from vNSFO

```
curl -ik https://127.0.0.1:8448/package/remove/cirros_vnfd -X DELETE
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
curl -ik https://127.0.0.1:8448/vnsf/config
```

#### Provide the running vNSFs

```
curl -ik https://127.0.0.1:8448/vnsf/running
```

#### Execute pre-defined action from a specific vNSF
```
curl -ki https://127.0.0.1:8448/vnsf/action -X POST \
     -H 'Content-Type: application/json' \
     -d '{ "vnsf_id": "2145d576-1b91-4cb1-9b76-77f2aeab21cd", "action": "set-policies", "params": { "policies": "<mspl-set xmlns=\"http://security.polito.it/shield/mspl\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://security.polito.it/shield/mspl mspl.xsd\"><it-resource id=\"2145d576-1b91-4cb1-9b76-77f2aeab21cd\"><configuration xsi:type=\"filtering-configuration\"><default-action>drop</default-action><resolution-strategy>FMR</resolution-strategy><rule><priority>101</priority><action>drop</action><condition><packet-filter-condition><direction>inbound</direction><direction>inbound</direction><source-address>10.30.0.190</source-address><protocol>UDP</protocol></packet-filter-condition><traffic-flow-condition><rate-limit>36kbit</rate-limit></traffic-flow-condition></condition></rule></configuration></it-resource></mspl-set>" } }'
```

# Testing

Run all tests, or either mocked or real-time/live tests.

```
cd test
python3 main.py
python3 main.py -m
python3 main.py -r
```
