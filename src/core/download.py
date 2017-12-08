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


from tempfile import mkdtemp
import os


def fetch_content(url):
    if not url.startswith("http"):
        return None
    tmp_folder = mkdtemp()
    tmp_file = url.split("/")[-1]
    tmp_path = os.path.join(tmp_folder, tmp_file)
    try:
        import urllib
        data = urllib.urlretrieve(url, tmp_path)
    except AttributeError:
        import urllib.request
        data = urllib.request.urlopen(url).read()
    f = open(tmp_path, "wb")
    f.write(data)
    f.close()
    return tmp_path
