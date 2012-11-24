# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
import urllib2
import json
import re
from collections import Counter

def home(request):
    data = api('media', 'popular')

    image_list = []
    comment_list = []
    likes_list = []
    filter_list = []
    filter_count = Counter()
    location_list = []
    caption_list = []
    tags_list = []
    dict_avg = {}
    for i in data:
        for x in json.loads(i)["data"]:
            comment_list.append( x["comments"]["count"])
	    likes_list.append(x["likes"]["count"])
	    filter_list.append( x["filter"])
            image_list.append(x["images"]["standard_resolution"]["url"])
	    filter_count[x["filter"]] += 1
	    location_list.append(x["location"])
	    #caption_list.append(x["caption"]["text"])
	    tags_list.append(x["tags"])

    #print images
    print comment_list
    print filter_list
    print filter_count
    print location_list
    #print caption_list
    print tags_list
 
    #print avg(float(x["comments"]["count"])}
 
    # avg # of comments
    avg_comments = sum(comment_list)/float(len(comment_list))
    avg_likes = sum(likes_list)/float(len(likes_list))

    dict_avg['comments'] = avg_comments
    dict_avg['likes'] = avg_likes
    dict_avg['urls'] = image_list
    print dict_avg

    return render_to_response('insta/index.html', dict_avg)
    #return HttpResponse("hello world")


def api(endpoint, type):
    # construct instagram api arcane_heroku
    api_url = "https://api.instagram.com/v1/%s/%s?client_id=" % (endpoint, type)
    client_id = "0e9b256777bd490697a334427d0dd72b"
    url = "%s%s" % (api_url, client_id)

    # get data from api
    data = urllib2.urlopen(url)
    
    return data
