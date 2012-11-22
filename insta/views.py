# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
import urllib2
import json
import re

def home(request):
    data = api()
 
    for i in data:
        for x in json.loads(i)["data"]:
            print x["comments"]["count"]
 
    return HttpResponse("hello world")


def api():
    # construct instagram api
    api_url = "https://api.instagram.com/v1/media/popular?client_id="
    client_id = "0e9b256777bd490697a334427d0dd72b"
    url = "%s%s" % (api_url, client_id)

    # get data from api
    data = urllib2.urlopen(url)
    
    return data
