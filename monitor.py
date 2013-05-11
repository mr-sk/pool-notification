#!/usr/bin/env python
# -----------------------------------------------------------------------------
# monitor.py
#
# Shoutz: All the BTC & LTC guys on the forums: zif, Delarock. 
#         efnet #innercircle, freenode #give-me-ltc
# Fuckz: MKEGuy <-- scammer!
#
# Author: sk / sk@mr-sk.com
# -----------------------------------------------------------------------------

import boto
import pprint
import config
import urllib2
import json
import sys
import pickle
import os

class Monitor:
    
    def __init__(self):
        self.inmemoryDict = {}
        self.loadedDict   = {}
        self.giveMeLTCAPI = 'https://give-me-ltc.com/api?api_key='
        if os.path.exists("workers.p"):
            self.loadedDict = pickle.load(open("workers.p", "rb"))
            print "[x] Loaded dictionary" 

    def sendAlert(self, msg):
        sns = boto.connect_sns()
        mytopic_arn = config.snsTopic
        res = sns.publish(mytopic_arn, msg, '')

    def heartbeat(self):
        req    = urllib2.Request(self.giveMeLTCAPI + config.poolKey)
        opener = urllib2.build_opener()

        for parentKey, subDict in json.loads(opener.open(req).read())['workers'].iteritems():
            if 'last_share_timestamp' in subDict:
                self.inmemoryDict[parentKey] = subDict['hashrate']

        if len(self.loadedDict.keys())< 1:
            print "[!] Loaded dictionary is empty, assign (Probably first time running)"
            pickle.dump(self.inmemoryDict, open("workers.p", "wb"))
            sys.exit()

        dictIter = self.loadedDict.iteritems()
        for wName, wHash in config.workerDict.iteritems():
            for lKey, lHash in dictIter:
                if wName not in self.inmemoryDict:
                    print "[!] Missing worker %s, sending alert" % wName
                    self.sendAlert("Worker %s has dropped off" % wName)
                if lKey in self.inmemoryDict:
                    print "[x] Worker %s current hash %s, threshold %s" % (lKey, lHash, wHash)
                    if int(lHash) < wHash:     
                        print "[!] Issue found with worker %s, sending alert" % lKey
                        self.sendAlert("Worker %s is below %s" % (lKey, wHash))
                    break

        pickle.dump(self.inmemoryDict, open("workers.p", "wb"))    
        print "[x] Complete\n"

#
# Main
#

monitor = Monitor()
monitor.heartbeat();
