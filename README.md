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

If HTTPS and/or client certificate is enabled, PKI data must be generated first:
```
./bin/gen_creds.sh
```
Similarly, configuration data must be copied from the provided samples:
```
./bin/set_conf.sh
```

## Docker

TBD

# Deployment

TODO

# API Documentation

The documentation follows the [OpenAPI Specification](https://swagger.io/specification/) (aka Swagger RESTful API Documentation Specification) Version 2.0 and is defined in the [api.yaml](src/server/api.yaml) file. Use [Swagger Editor](https://editor.swagger.io/) for a user-friendly view.

# Testing

TODO
