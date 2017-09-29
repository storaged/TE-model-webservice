#!/usr/bin/python
import requests
import sys
import pycurl 


HOST        = 'wloczykij'
USER        = 'sftp://transp'
WEBSERV_DIR = '/home/transp/simulations/webservice/'
PATH_TO_KEY = '/home/krzysiek/.ssh/id_rsa'

MODEL_ID    = sys.argv[1]
BATCH_RUN   = sys.argv[2]
IMG_NAME    = "plot-3.png"

url   = USER + "@" + HOST + ":" + WEBSERV_DIR + 'model-transposons-' + MODEL_ID + "/batch-run-" + BATCH_RUN + "/" + IMG_NAME

c = pycurl.Curl()
c.setopt(c.URL, url)
c.perform()
