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

## Docker

TBD

# Deployment

TODO

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

#### Provide avialable NSs

```
curl -ik https://127.0.0.1:8448/ns/running
```

### Package

#### Onboards a locally stored package into NFVO

```
curl -ik https://127.0.0.1:8448/package/onboard -X POST -F "package=@/tmp/cirros_vnf.tar.gz"
```

#### Onboards a remotely stored package into NFVO

```
curl -ik https://127.0.0.1:8448/package/onboard/remote -H "Content-Type: application/json" -X POST -d '{"path": "https://osm-download.etsi.org/ftp/examples/cirros_2vnf_ns/cirros_vnf.tar.gz"}'

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
curl -ik -H "Content-Type: multipart/form-data" -F "image=@/tmp/Fedora-x86_64-20-20131211.1-sda-ping.qcow2" -X POST https://127.0.0.1:8448/vim/image/$vim_id
```

### vNSF

#### Provide the running vNSFs

```
curl -ik https://127.0.0.1:8448/vnsf/running
```

#### Execute pre-defined action from a specific vNSF
```
curl -ki -H 'Content-Type: application/json' -X POST https://127.0.0.1:8448/vnsf/action -d '{ "action": "set-policies", "params": { "policies": "<mspl-set xmlns=\"http://security.polito.it/shield/mspl\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://security.polito.it/shield/mspl mspl.xsd\"><it-resource id=\"2145d576-1b91-4cb1-9b76-77f2aeab21cd\"><configuration xsi:type=\"filtering-configuration\"><default-action>drop</default-action><resolution-strategy>FMR</resolution-strategy><rule><priority>101</priority><action>drop</action><condition><packet-filter-condition><direction>inbound</direction><direction>inbound</direction><source-address>10.30.0.190</source-address><protocol>UDP</protocol></packet-filter-condition><traffic-flow-condition><rate-limit>36kbit</rate-limit></traffic-flow-condition></condition></rule></configuration></it-resource></mspl-set>" } }'
```

# Testing

Run either mocked or real-time/live tests, or all of them.

```
cd test
python main.py -m
python main.py -r
python main.py
```

