# vNSFO API

The vNSFO used in SHIELD consists of the [OSM MANO](https://osm.etsi.org) on one hand, and on a lightweight API that implements extra functionalities demanded by the project.

The orchestrator is a central element which covers the deployment of the Virtual Network Secure Functions (vNSF) provided by SHIELD and its lifecycle management. The API provides means to interact with other components of the SHIELD platform, e.g. pushing configurations in Medium Security Policy Language (MSPL) and exert them to specific vNSF.

# Installation

## Prerequisites

* [Python 3](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [MongoDB](https://www.mongodb.com/)
* [Requests](http://docs.python-requests.org/en/master/)
* [PyYAML](http://pyyaml.org/) to handle vNSF and NS descriptors

## First set-up

If HTTPS and/or client certificate is enabled, PKI data must be generated first.
```
./bin/gen_creds.sh
```
Similarly, configuration data must be copied from the provided samples. This will fill with the proper IPs. **Note** that the vNSFO must run in the same host as OSM.
```
./bin/set_conf.sh
```
The dependencies can be installed through a script.
```
./bin/deploy.sh
```

## Docker

TBD

# Deployment

TODO

# API Documentation

The documentation follows the [OpenAPI Specification](https://swagger.io/specification/) (aka Swagger RESTful API Documentation Specification) version 2.0.
It is defined in the [endpoints.yaml](src/server/endpoints.yaml) file; and can be consulted in a user-friendly way by pointing your browser to the root of the vNSFO API server or directly paste the contents into [Swagger Editor](https://editor.swagger.io/).

# Testing

TODO
