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


from flask import Blueprint
from flask import render_template

import os
import json
import yaml


swaggerui_folder = os.path.normpath(
        os.path.join(os.path.dirname(__file__),
                     "../../src/gui", "flask_swagger_ui"))
template_folder = os.path.normpath(os.path.join(swaggerui_folder, "templates"))
static_folder = os.path.normpath(os.path.join(swaggerui_folder, "dist"))

swagger_views = Blueprint(
        "swagger_ui",
        __name__,
        static_folder=static_folder,
        template_folder=template_folder)


def generate_swagger_spec_file():
    # Read Swagger YaML file, parse to JSON
    yaml_def = open(os.path.normpath(
        os.path.join(static_folder, "../../../server/endpoints.yaml")))\
        .read()
    swagger_json = json.dumps(yaml.load(yaml_def), sort_keys=True, indent=2)
    # Save to specific JS file, to be loaded by flask-swagger-ui
    swagger_json_f = open(os.path.normpath(
        os.path.join(static_folder, "spec.js")), "w")
    swagger_json_f.write("var spec={}".format(swagger_json))
    swagger_json_f.close()


def generate_swagger_docs(base_url="/", api_url=""):
    generate_swagger_spec_file()
    default_config = {
        "app_name": "Swagger UI",
        "dom_id": "#swagger-ui",
        "url": api_url,
        "layout": "StandaloneLayout",
        "validatorUrl": "null"
    }
    # Some fields are used directly in template (base_url, app_name)
    # Others serialized into json string for inclusion in the .js file
    fields = {"base_url": base_url, "app_name": "SHIELD vNSFO REST API",
              "config_json": json.dumps(default_config)}
    return render_template("index.template.html", **fields)
