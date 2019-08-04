#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# simple EH api test
# Now it's part of my exh db update tool :)

import json, urllib, sys
import os
import io
import re
import time
import getopt

cookie = "ipb_member_id=9999999;ipb_pass_hash=ffffffffffffffff"

# python 2 vs. python 3 compatibility
try:
    from http import client as httpclient
except ImportError:
    import httplib as httpclient

oldestTimestamp = int(time.time())
nextLatestTimestamp = 0

reqpy = { "method"  : "gdata"
        , "gidlist" : [ [ 639967 , "e2be237948" ]
                      ]
        , "namespace" : 1
        }

headers = { 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36' \
          , "Accept"       : "application/jsonrequest" \
          , "Content-type" : "text/json" \
          , "Cookie": cookie
          }

headers4search = { 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36' \
          , "Accept"       : "application/jsonrequest" \
          , "Content-type" : "*/*" \
          , "Cookie": cookie
          }

respJs = {}

def getSearchHtml(page):
  conn  = httpclient.HTTPSConnection("exhentai.org")
  conn.request("GET", "/?page=" + str(page) + "&f_cats=0&f_sname=on&f_stags=on&f_sh=on&advsearch=1", "", headers);
  reply = conn.getresponse()
  data  = reply.read()
  print(reply.status, reply.reason)
  if(reply.status != 200):
    conn.close()
    print("ERROR while getting search result!")
    print("Will retry after 5s...")
    time.sleep(5)
    return getSearchHtml(page)
  conn.close()
  return data

def setlist(htmldoc):
  gurls = re.findall("/g/[0-9]+/[0-9a-zA-Z]+/", htmldoc)
  #print(gurls)
  global reqpy
  gidlist = []
  for url in gurls:
    a1, a2, a3, a4, a5 = url.split('/')
    a3 = int(a3)
    gidlist.append([a3, a4])
  print(gidlist)
  reqpy['gidlist'] = gidlist

def process():
  global oldestTimestamp, reqpy, headers, respJs, nextLatestTimestamp

  req = json.dumps(reqpy)

  conn  = httpclient.HTTPSConnection("exhentai.org")
  conn.request("POST", "/api.php", req, headers);
  reply = conn.getresponse()
  data  = reply.read()
  print(reply.status, reply.reason)
#  print(data)

  response = json.loads(data)
  glist = response['gmetadata']
  for i in range(len(glist)):
    if(int(glist[i]['posted']) < oldestTimestamp):
      oldestTimestamp = int(glist[i]['posted'])
    if(int(glist[i]['posted']) > nextLatestTimestamp):
      nextLatestTimestamp = int(glist[i]['posted'])
    respJs[glist[i]['gid']] = glist[i]

#  print(response)
  conn.close()
#
#  json.dump(respJs, io.open("tmp.json", "w", encoding="utf-8"))
#
def writeTmp(outputfile):
  global respJs
  with io.open(outputfile, "w", encoding="utf-8") as outf:
    outf.write(unicode(json.dumps(respJs, ensure_ascii=False)))

def main(argv):
  global nextLatestTimestamp, cookie, headers4search, headers
  latestPosted = 0
  ipb_member_id = "9999999"
  ipb_pass_hash = "ffffffffffffffff"
  outputfile = "gdata.json"
  timed = True
  opts, args = getopt.getopt(argv,"ht:o:m:p:")
  for opt, arg in opts:
    if (opt == '-h'):
        print(sys.argv[0] + ' [-t <OldestTimestamp to Search>] [-o <outputfile>] [-m <ipb_member_id>] [-p <ipb_pass_hash>]')
        print(" -t <timestamp>: Oldest timestamp to search. Default: input from file 'latestPosted'")
        print(" -o <filename>: Output file name. Default: gdata.json")
        print(" -m <ipb_member_id>: Set 'ipb_member_id' of cookie manually. Default:9999999 (Unusable)")
        print(" -p <ipb_pass_hash>: Set 'ipb_pass_hash' of cookie manually. Default:ffffffffffffffff (Unusable)")
        sys.exit()
    elif (opt == "-t"):
        latestPosted = int(arg)
        timed = False
    elif (opt == "-o"):
        outputfile = str(arg)
    elif (opt == "-m"):
        ipb_member_id = str(arg)
    elif (opt == "-p"):
        ipb_pass_hash = str(arg)

  cookie = ("ipb_member_id=" + str(ipb_member_id) + ";ipb_pass_hash=" + str(ipb_pass_hash))
  headers4search = { 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36' \
          , "Accept"       : "application/jsonrequest" \
          , "Content-type" : "*/*" \
          , "Cookie": cookie
          }
  headers = { 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36' \
          , "Accept"       : "application/jsonrequest" \
          , "Content-type" : "text/json" \
          , "Cookie": cookie
          }

  if(timed):
    if(os.path.exists("latestPosted") != True):
       print("WARNNING: Cannot find latestPosted cache, and -t isnt given neither.")
       print("So we will search until timestamp 1174358472 when gid=9 was posted.")
       latestPosted=1174358472
    else:
      with io.open("latestPosted", "r") as f:
        latestPosted = int(f.read())
        print("Read latestPosted from file as " + str(latestPosted))
        f.close()

  print("Latest gallery given was posted at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(latestPosted)))
  nextLatestTimestamp = latestPosted
  page=0
  global oldestTimestamp
  while(oldestTimestamp > latestPosted):
    print("Now oldest " + str(oldestTimestamp) +" > " + str(latestPosted))
    print("Requesting search page " + str(page+1) + "...")
    searchHTML = getSearchHtml(page)
    setlist(searchHTML)
    process()
    page = page+1
  print("Done. We ve got gallery posted at " + str(oldestTimestamp) + " <= " + str(latestPosted))

  print("Writing json to file " + outputfile + "...")
  writeTmp(outputfile)
  print("Done.")
  
  print("Now refresh latestPosted as " + str(nextLatestTimestamp) + "...")
  os.remove("latestPosted")
  with io.open("latestPosted", "w") as f:
    f.write(unicode(str(nextLatestTimestamp)))
    f.close()
  print("Done.")


if __name__ == '__main__':
  main(sys.argv[1:])
