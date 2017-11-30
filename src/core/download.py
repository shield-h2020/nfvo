#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    except:
        import urllib.request
        data = urllib.request.urlopen(url).read()
        f = open(tmp_path, "wb")
        f.write(data)
        f.close()
    return tmp_path
