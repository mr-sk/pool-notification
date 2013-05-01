#!/usr/bin/env python
# -----------------------------------------------------------------------------
# monitor.py
#
# Shoutz: All the BTC & LTC guys on the forums: MKEGuy, zif, Delarock. 
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
for lKey, lHash in loadedDict.iteritems():
    if inmemoryDict[lKey] <= config.hashMin and lHash <= config.hashMin:     
        print "[!] Issue found with worker %s, sending alert" % lKey
        sns = boto.connect_sns()
        msg         = "Worker %s is below %s" % (lKey, config.hashMin)
        mytopic_arn = config.snsTopic
        res = sns.publish(mytopic_arn, msg, '')

pickle.dump(inmemoryDict, open("workers.p", "wb"))    
print "Complete\n"
