var spec={
  "basePath": "/", 
  "definitions": {
    "ConfigNssOutput": {
      "items": {
        "properties": {
          "ns": {
            "properties": {
              "name": {
                "example": "cirros_2vnf_nsd", 
                "type": "string"
              }, 
              "ns_id": {
                "example": "cirros_2vnf_nsd", 
                "type": "string"
              }, 
              "vendor_id": {
                "example": "OSM", 
                "type": "string"
              }
            }, 
            "required": [
              "name", 
              "ns_id", 
              "vendor_id"
            ], 
            "type": "object"
          }
        }, 
        "required": [
          "ns"
        ], 
        "type": "object"
      }, 
      "type": "array"
    }, 
    "EndPoints": {
      "properties": {
        "endpoints": {
          "items": {
            "properties": {
              "endpoint": {
                "example": "/", 
                "type": "string"
              }, 
              "methods": {
                "items": {
                  "example": "GET", 
                  "type": "string"
                }, 
                "type": "array"
              }
            }, 
            "type": "object"
          }, 
          "type": "array"
        }
      }, 
      "required": [
        "endpoints"
      ], 
      "type": "object"
    }, 
    "RunningVnsfOutput": {
      "items": {
        "properties": {
          "name": {
            "example": "mspl__mspl_vnf__2", 
            "type": "string"
          }, 
          "ns_id": {
            "example": "84e9676d-a237-4908-86e9-60eb976dae3c", 
            "type": "string"
          }, 
          "vendor": {
            "example": "SHIELD", 
            "type": "string"
          }, 
          "vnf_id": {
            "example": "ed37f789-9ed8-43bc-8b5f-c4c1ca192363", 
            "type": "string"
          }
        }, 
        "type": "object"
      }, 
      "type": "array"
    }, 
    "VimRegisterImageInput": {
      "properties": {
        "img_checksum": {
          "example": "...", 
          "type": "string"
        }, 
        "img_url": {
          "example": "...", 
          "type": "string"
        }
      }, 
      "required": [
        "img_url", 
        "img_checksum"
      ], 
      "type": "object"
    }, 
    "VimRegisterImageOutput": {
      "properties": {
        "img_checksum": {
          "type": "string"
        }, 
        "img_url": {
          "type": "string"
        }
      }, 
      "required": [
        "img_url", 
        "img_checksum"
      ], 
      "type": "object"
    }, 
    "VnsfActionInput": {
      "properties": {
        "action": {
          "example": "set-policies", 
          "type": "string"
        }, 
        "params": {
          "example": {
            "key": "value"
          }, 
          "type": "object"
        }, 
        "vnsf_id": {
          "example": "afcb3492-f326-4979-acea-fcc47168ca12", 
          "type": "string"
        }
      }, 
      "required": [
        "vnsf_id", 
        "action", 
        "params"
      ], 
      "type": "object"
    }, 
    "VnsfActionOutput": {
      "properties": {
        "output": {
          "properties": {
            "create-time": {
              "example": "1505647110", 
              "type": "string"
            }, 
            "job-id": {
              "example": "1", 
              "type": "string"
            }, 
            "name": {
              "type": "string"
            }, 
            "nsr_id_ref": {
              "example": "e3c04a54-2a4b-4bd7-84d0-f0c024857380", 
              "type": "string"
            }, 
            "triggered-by": {
              "example": "ns-primitive", 
              "type": "string"
            }, 
            "vnf-out-list": {
              "properties": {
                "member_vnf_index_ref": {
                  "example": "1", 
                  "type": "string"
                }, 
                "vnf-out-primitive": {
                  "properties": {
                    "execution-error-details": {
                      "example": "", 
                      "type": "string"
                    }, 
                    "execution-id": {
                      "example": "action-2ac6e694-b347-411a-839d-fca863b2ea1a", 
                      "type": "string"
                    }, 
                    "execution-status": {
                      "example": "pending", 
                      "type": "string"
                    }, 
                    "index": {
                      "example": "0", 
                      "type": "string"
                    }, 
                    "name": {
                      "example": "set-policies", 
                      "type": "string"
                    }, 
                    "parameter": {
                      "properties": {
                        "name": {
                          "example": "policies", 
                          "type": "string"
                        }, 
                        "value": {
                          "example": "<xml>data</xml>", 
                          "type": "string"
                        }
                      }, 
                      "required": [
                        "name", 
                        "value"
                      ], 
                      "type": "object"
                    }, 
                    "vnfr-id-ref": {
                      "example": "afcb3492-f326-4979-acea-fcc47168ca12", 
                      "type": "string"
                    }
                  }, 
                  "required": [
                    "execution-error-details", 
                    "execution-id", 
                    "execution-status", 
                    "index", 
                    "name", 
                    "parameter", 
                    "vnfr-id-ref"
                  ], 
                  "type": "object"
                }
              }, 
              "required": [
                "member_vnf_index_ref", 
                "vnf-out-primitive"
              ], 
              "type": "object"
            }
          }, 
          "type": "object"
        }
      }, 
      "required": [
        "output"
      ], 
      "type": "object"
    }
  }, 
  "externalDocs": {
    "description": "Find out more about the vNSFO API", 
    "url": "https://github.com/shield-h2020/vnsfo"
  }, 
  "host": "TBD", 
  "info": {
    "contact": {
      "email": "carolina.fernandez@i2cat.net"
    }, 
    "description": "This API provides interaction between OSM and the SHIELD components. Some of the functionality provided are the proxying of MSPL for configuration towards specific vNSFs.</p>", 
    "license": {
      "name": "License - TBD", 
      "url": "http://TBD"
    }, 
    "termsOfService": "", 
    "title": "vNSFO API", 
    "version": "0.1.0"
  }, 
  "paths": {
    "/": {
      "get": {
        "description": "<p>All available REST methods are provided through this method.</p>", 
        "operationId": "getEntryPoints", 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded", 
            "schema": {
              "$ref": "#/definitions/EndPoints"
            }
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Lists all the API methods", 
        "tags": [
          "common"
        ]
      }
    }, 
    "/nfvi/config/nss": {
      "get": {
        "description": "<p>Returns the available NSs.</p>", 
        "operationId": "getAvailableNss", 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded", 
            "schema": {
              "$ref": "#/definitions/ConfigNssOutput"
            }
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Provides the available NSs", 
        "tags": [
          "nfvi"
        ]
      }
    }, 
    "/nfvi/flowtable": {
      "get": {
        "description": "<p>TBD. Provides the contents of the flow tables of the SDN controller.</p>", 
        "operationId": "getDevicesFlowtable", 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded."
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Provides the flow tables in the network devices", 
        "tags": [
          "nfvi"
        ]
      }
    }, 
    "/nfvi/nodes": {
      "get": {
        "description": "<p>TBD. Provides the list of active physical nodes in the NFVI.</p>", 
        "operationId": "getDeployedPhysicalNodes", 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded."
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Provides the physical nodes in the NFVI", 
        "tags": [
          "nfvi"
        ]
      }
    }, 
    "/nfvi/running/vnsfs": {
      "get": {
        "description": "<p>Returns the deployed vNSFs.</p>", 
        "operationId": "getDeployedVnsfs", 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded", 
            "schema": {
              "$ref": "#/definitions/RunningVnsfOutput"
            }
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Provides the deployed vNSFs", 
        "tags": [
          "nfvi"
        ]
      }
    }, 
    "/nfvi/running/vnsfs/{tenant}": {
      "get": {
        "description": "<p>TBD. Returns the deployed vNSFs per tenant.</p>", 
        "operationId": "getDeployedVnsfsPerTenant", 
        "parameters": [
          {
            "in": "path", 
            "name": "tenant", 
            "required": true, 
            "type": "string"
          }
        ], 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded."
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Provides the deployed vNSFs per tenant", 
        "tags": [
          "nfvi"
        ]
      }
    }, 
    "/nfvi/topology": {
      "get": {
        "description": "<p>TBD. Returns the topology of the network as known to the VIM.</p>", 
        "operationId": "getNetworkTopology", 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded."
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Provides the network topology", 
        "tags": [
          "nfvi"
        ]
      }
    }, 
    "/vim/vnsf_image": {
      "post": {
        "consumes": [
          "application/json"
        ], 
        "description": "<p>TBD. Uploads the image of a vNSF into the VIM.</p>", 
        "operationId": "registerVnsfImage", 
        "parameters": [
          {
            "description": "The body of the request", 
            "in": "body", 
            "name": "body", 
            "required": true, 
            "schema": {
              "$ref": "#/definitions/VimRegisterImageInput"
            }
          }
        ], 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded", 
            "schema": {
              "$ref": "#/definitions/VimRegisterImageOutput"
            }
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Registers vNSF image into the VIM", 
        "tags": [
          "vim"
        ]
      }
    }, 
    "/vnsf/action": {
      "post": {
        "consumes": [
          "application/json"
        ], 
        "description": "<p>Triggers the remote execution of data into a specific vNSF.</p>", 
        "operationId": "executeVnsfAction", 
        "parameters": [
          {
            "description": "The body of the request", 
            "in": "body", 
            "name": "body", 
            "required": true, 
            "schema": {
              "$ref": "#/definitions/VnsfActionInput"
            }
          }
        ], 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded", 
            "schema": {
              "$ref": "#/definitions/VnsfActionOutput"
            }
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Executes pre-defined action from a specific vNSF", 
        "tags": [
          "vnsfs"
        ]
      }
    }, 
    "/vnsf/{vnsf}/action/{action}": {
      "get": {
        "description": "<p>TBD. Checks the status of the remote execution of data into a specific vNSF.</p>", 
        "operationId": "checkVnsfAction", 
        "parameters": [
          {
            "description": "ID of the vNSF record", 
            "in": "path", 
            "name": "vnsf", 
            "required": true, 
            "type": "string"
          }, 
          {
            "description": "ID of the action executed", 
            "in": "path", 
            "name": "action", 
            "required": true, 
            "type": "string"
          }
        ], 
        "produces": [
          "application/json"
        ], 
        "responses": {
          "200": {
            "description": "Request succeeded."
          }, 
          "400": {
            "description": "Bad request. API specific parameters are incorrect or missing."
          }, 
          "404": {
            "description": "Not found. The requested resource doesn't exist."
          }, 
          "418": {
            "description": "Improper usage of the resource."
          }
        }, 
        "summary": "Fetches the status of an executed pre-defined action into a specific vNSF", 
        "tags": [
          "vnsfs"
        ]
      }
    }
  }, 
  "responses": {
    "200": {
      "description": "Request succeeded."
    }, 
    "400": {
      "description": "Bad request. API specific parameters are incorrect or missing."
    }, 
    "404": {
      "description": "Not found. The requested resource doesn't exist."
    }, 
    "418": {
      "description": "Improper usage of the resource."
    }
  }, 
  "schemes": [
    "https"
  ], 
  "swagger": "2.0", 
  "tags": [
    {
      "description": "Common operations", 
      "name": "common"
    }, 
    {
      "description": "Deployment data", 
      "externalDocs": {
        "description": "D3.1", 
        "url": "https://www.shield-h2020.eu/documents/project-deliverables/SHIELD_D3.1_Specifications,_Design_and_Architecture_for_the_vNSF_Ecosystem_v1.0.pdf"
      }, 
      "name": "nfvi"
    }, 
    {
      "description": "VIM operations", 
      "externalDocs": {
        "description": "OSMr2 API", 
        "url": "https://osm.etsi.org/wikipub/images/2/24/Osm-r1-so-rest-api-guide.pdf"
      }, 
      "name": "vim"
    }, 
    {
      "description": "vNSF operations", 
      "externalDocs": {
        "description": "OSMr2 API", 
        "url": "https://osm.etsi.org/wikipub/images/2/24/Osm-r1-so-rest-api-guide.pdf"
      }, 
      "name": "vnsfs"
    }
  ]
}