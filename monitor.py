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

inmemoryDict = {}
loadedDict   = {}
if os.path.exists("workers.p"):
    loadedDict = pickle.load(open("workers.p", "rb"))
    print "[x] Loaded dictionary" 

giveMeLTCAPI = 'https://give-me-ltc.com/api?api_key='
req    = urllib2.Request(giveMeLTCAPI + config.poolKey)
opener = urllib2.build_opener()

for parentKey, subDict in json.loads(opener.open(req).read())['workers'].iteritems():
   if 'last_share_timestamp' in subDict:
       inmemoryDict[parentKey] = subDict['hashrate']

if len(loadedDict.keys())< 1:
    print "[!] Loaded dictionary is empty, assign (Probably first time running)"
    pickle.dump(inmemoryDict, open("workers.p", "wb"))
    sys.exit()

# Two dictionaries with values, compare the hash values in each
# and make sure they don't both fall below the threshold. 
dictIter = loadedDict.iteritems()
for wName, wHash in config.workerDict.iteritems():
    for lKey, lHash in dictIter:
        if inmemoryDict[lKey]:
            if int(lHash) < wHash:     
                print "[!] Issue found with worker %s, sending alert" % lKey
                sns = boto.connect_sns()
                msg         = "Worker %s is below %s" % (lKey, wHash)
                mytopic_arn = config.snsTopic
                res = sns.publish(mytopic_arn, msg, '')
        break

pickle.dump(inmemoryDict, open("workers.p", "wb"))    
print "[x] Complete\n"
