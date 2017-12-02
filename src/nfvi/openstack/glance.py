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


from glanceclient import Client
from hashlib import md5


class OpenStackGlance:
    """
    Adaptor to connect to OpenStack's Glance service.
    Reference: https://docs.openstack.org/python-glanceclient/latest/reference
    """

    def __init__(self, os_conn):
        self.GLANCE_VERSION = "1"
        self.key_session = os_conn.key_session
        self.client = Client(
                self.GLANCE_VERSION, session=self.key_session)

    def __check_vdu_uploaded(self, checksum, images=None):
        if images is None:
            images = self.get_images()
        for image in images:
            if checksum == image.checksum:
                return image
        return None

    def get_images(self):
        image_list = self.client.images.list()
        return [x for x in image_list]

    def upload_image(self, img_name, img_bin):
        img_bin_r = img_bin.read()
        # Reading the first memory page is enough for the hash
        # But img is to be fully read at least once, so...
        # ://joelverhagen.com/blog/2011/02/md5-hash-of-file-in-python
        # img_bin_r = img_bin.read(8192)
        checksum = md5(img_bin_r).hexdigest()
        vdu_remote = self.__check_vdu_uploaded(checksum)
        status = "failure"
        # VDU image is not already registered in the remove VIM, and
        # can thus be uploaded
        if vdu_remote is None:
            vdu_remote = self.client.images.create(
                    name=img_name, is_public=True, disk_format="qcow2",
                    container_format="bare", data=img_bin_r)
            status = "success"
        # Using "with" for img_bin can block the img file read
        # Rather close that manually
        img_bin.close()
        return (status, vdu_remote)
