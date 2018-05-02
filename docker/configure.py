#!/usr/bin/env python
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

import configparser

from jinja2 import Template


def read_config_files(confd):
    """
    Reads configuration files

    @param confd Configuration description dictionary (filepaths)
    @return confs Configuration objects dictionary
    """
    confs = {}
    for key in confd.keys():
        confs[key] = configparser.ConfigParser()
        confs[key].read(confd[key])
    return confs


def apply_confs(confs):
    """
    Render configuration templates

    @param confs Configuration objects dictionary
    @return None
    """
    dc_templ = Template(open("docker/docker-compose.yml.template").read())
    dc_render = dc_templ.render({'mongo_initdb_root_username':
                                 confs["db"]["db"]["admin_username"],
                                 'mongo_initdb_root_password':
                                 confs["db"]["db"]["admin_password"],
                                 'mongo_initdb_database':
                                 confs["db"]["db"]["auth_source"],
                                 "nfvo_port":
                                 confs["api"]["general"]["port"]})

    with open("docker/docker-compose.yml", "w") as outfile:
        outfile.write(dc_render.replace("\t", "    "))
    au_templ = Template(
        open("docker/mongo-entrypoint/adduser.sh.template").read())

    with open("docker/mongo-entrypoint/adduser.sh", "w") as outfile:
        outfile.write(
            au_templ.render({'mongo_initdb_root_username':
                             confs["db"]["db"]["admin_username"],
                             'mongo_initdb_root_password':
                             confs["db"]["db"]["admin_password"],
                             'mongo_initdb_database':
                             confs["db"]["db"]["auth_source"],
                             'db_username':
                             confs["db"]["db"]["user"],
                             'db_password':
                             confs["db"]["db"]["password"],
                             'db_dbname':
                             confs["db"]["db"]["name"]}))

if __name__ == "__main__":
    CONFS = read_config_files({"api": "conf/api.conf",
                               "db": "conf/db.conf",
                               "nfvo": "conf/nfvo.conf"})
    apply_confs(CONFS)
