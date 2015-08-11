#
# Automatically sync local folders on m0 with those on m1.
#
# Hao Wu (hao.wu@graphsql.com)
# Created: 05/12/2015, modified: 05/15/2015
#
# Usage of watchdog:
#     1) https://pypi.python.org/pypi/watchdog
#     2) http://goo.gl/qevcdV (on StackOverflow)
#
# Documentation of this script:
#     https://www.evernote.com/l/AAdW7Jj0hMBM-aDNnVDAwUtVPuBHsK3b44k
#

import os
import sys
import json
import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#
##
#

class Hop:
    #
    def __init__(self, name, user, host, key):
        #
        self.name = name
        self.user = user
        self.host = host
        self.key = key

#
##
#

class Link:
    #
    def __init__(self, name, folder_src, folder_tar, v_hop):
        #
        self.name = name
        self.folder_src = folder_src
        self.folder_tar = folder_tar
        self.v_hop = v_hop
        #
        if self.folder_src[-1] != '/':
            self.folder_src.append('/')

#
##
#

class MyEventHandler(FileSystemEventHandler):
    #
    def __init__(self, link):
        #
        self.link = link
    #
    def on_modified(self, event):
        #
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print "[%s] %s: Syncing ......" % (ts, self.link.name)
        cmd = "rsync -a -e \""
        n_hop = len(self.link.v_hop)
        for i in range(0, n_hop):
            cmd += "ssh "
            if i < n_hop - 1:
                cmd += "-X "
            hop = self.link.v_hop[i]
            cmd += "-i %s %s@%s" % (hop.key, hop.user, hop.host)
            if i < n_hop - 1:
                cmd += " "
        cmd += "\" --exclude '.*' %s :%s" \
               % (self.link.folder_src, self.link.folder_tar)
        #print cmd
        os.system(cmd)
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print "[%s] %s: Synced." % (ts, self.link.name)

#
##
#

def main():
    #
    if len(sys.argv) != 2:
        print "Usage: python syncd.py <jsonfile>"
        return
    #
    d_hop = {}
    d_link = {}
    cfg = json.load(open(sys.argv[1], "r"))
    for x in cfg["hops"]:
        hop = Hop(x["name"], x["user"], x["host"], x["key"])
        d_hop[hop.name] = hop
    for x in cfg["links"]:
        if x["enabled"] is False:
            continue
        v_hop = []
        for y in x["hops"]:
            v_hop.append(d_hop[y])
        link = Link(x["name"], x["folder_src"], x["folder_tar"], v_hop)
        d_link[link.name] = link
    #
    observer = Observer()
    for linkname, link in d_link.items():
        observer.schedule(MyEventHandler(link), link.folder_src, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

#
##
#

if __name__ == "__main__":
    #
    main()

#
##
###
##
#
#
##
###
##
#
#
##
###
##
#
#
##
###
##
#
#
##
###
##
#

