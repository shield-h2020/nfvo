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


try:
    from StringIO import StringIO
    import ConfigParser
except ImportError:
    from io import StringIO
    from configparser import ConfigParser
import json
import logging as log
import os
import sys

logger = log.getLogger("config-parser")


class BaseParser:

    def __init__(self, path):
        """
        Constructor. Reads and parses every setting defined in a config file.

        @param path name of the configuration file
        @throws Exception when configuration directive is wrongly processed
        """
        self.settings = {}
        self.path = os.path.abspath(os.path.join(os.path.split(
            os.path.abspath(__file__))[0], "../../conf", path))

    def get(self, key):
        """
        Access internal dictionary and retrieve value from given key.

        @param key dictionary key to access
        @return value for desired key
        """
        value = self.__dict__.get(key, None)
        if any(map(lambda x: key.endswith(x), [".conf", ".json"])) and not value:
            exc_det = "Error retrieving configuration. Missing " + \
                "file {}/{}".format(self.path, key)
            logger.critical(exc_det)
            sys.exit(exc_det)
        return value


class ConfParser(BaseParser):

    def __init__(self, path):
        """
        Constructor. Reads and parses every setting defined in a config file.

        @param path name of the configuration file
        @throws Exception when configuration directive is wrongly processed
        """
        BaseParser.__init__(self, path)
        try:
            try:
                confparser = ConfigParser.SafeConfigParser()
            except:
                confparser = ConfigParser()
            # Parse data previously to ignore tabs, spaces or others
            conf_data = StringIO("\n".join(l.strip() for l in open(self.path)))
            parse_ok = True
            try:
                confparser.readfp(conf_data)
            # Error reading: eg. bad value substitution (bad format in strings)
            except ConfigParser.InterpolationMissingOptionError as e:
                confparser.read(conf_data)
                parse_ok = False
            # Do some post-processing of the conf sections
            self.__process_conf_sections(confparser, parse_ok)
        except Exception as e:
            exception_desc = "Could not parse configuration file '%s'. Details:\
                %s" % (str(self.path), str(e))
            logger.exception(exception_desc)
            print(exception_desc)
            sys.exit(exception_desc)
        self.__dict__.update(self.settings)

    def __process_conf_sections(self, confparser, parse_ok):
        """
        Parses every setting defined in a config file.

        @param confparser ConfigParser object
        @throws Exception when configuration directive is wrongly processed
        """
        for section in confparser.sections():
            self.settings[section] = {}
            try:
                confparser_items = confparser.items(section)
            except:
                confparser_items = confparser._sections.items()
                parse_ok = False
            for (key, val) in confparser_items:
                if parse_ok:
                    if key == "topics":
                        try:
                            val = [v.strip() for v in val.split(",")]
                        except:
                            exception_desc = "Could not process topics: \
                                %s" % str(val)
                            logger.exception(exception_desc)
                            sys.exit(exception_desc)
                    self.settings[section][key] = val
                else:
                    try:
                        for v in val.items():
                            if v[0] != "__name__":
                                self.settings[section][v[0]] = \
                                    str(v[1]).replace('\"', '')
                    except Exception as e:
                        exception_desc = "Cannot process item: %s. \
                            Details: %s" % str(val, e)
                        logger.exception(exception_desc)
                        sys.exit(exception_desc)


class JSONParser(BaseParser):

    def __init__(self, path):
        """
        Constructor. Reads the JSON config file.

        @param path name of the configuration file
        @throws Exception when configuration directive is wrongly processed
        """
        BaseParser.__init__(self, path)
        try:
            with open(self.path) as data_file:
                self.settings = json.load(data_file)
        except Exception as e:
            exception_desc = "Could not parse JSON configuration file '%s'. \
                Details: %s" % (str(self.path), str(e))
            logger.exception(exception_desc)
            sys.exit(exception_desc)
        self.__dict__.update(self.settings)


class FullConfParser(BaseParser):

    def __init__(self):
        BaseParser.__init__(self, "")
        self.__load_files()

    def __load_files(self):
        for f in os.listdir(self.path):
            if f.endswith(".conf"):
                self.__dict__.update({str(f): ConfParser(f).settings})
            elif f.endswith(".json"):
                self.__dict__.update({str(f): JSONParser(f).settings})
