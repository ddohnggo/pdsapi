# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
import urllib2
import json
import re
import requests
from collections import Counter, defaultdict

def home(request):
    data = insta_api('media', 'popular')

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


def insta_api(endpoint, *args):
    base_url = "https://api.instagram.com/v1/"
    client_id = "0e9b256777bd490697a334427d0dd72b"
    # construct instagram api arcane_heroku
    if endpoint == 'media':
        type = args[0]
        api_url = base_url + "%s/%s?client_id=" % (endpoint, type)
        url = "%s%s" % (api_url, client_id)

        # get data from api
        data = urllib2.urlopen(url)
    
    elif endpoint == 'locations':
        if args[0] == 'media':
	    data = []
	    # process places photos, return list of urls
	    for i in args[1]:
	        place_id = int(i)
	        api_url = base_url + "%s/%i/%s/recent?client_id=" % (endpoint, place_id, args[0])
	        url = "%s%s" % (api_url, client_id)
		data.append(url)

	else: 
            lat = args[0]
	    long = args[1]
            api_url = base_url + "%s/search?lat=%f&lng=%f&client_id=" % (endpoint, lat, long)
	    url = "%s%s" % (api_url, client_id)
	    print url
	
	    # get data from api
            data = urllib2.urlopen(url)

    return data
    


def location(request):
    # get ip address
    r = requests.get(r'http://jsonip.com')
    ip = r.json['ip']
    data = loc_api(ip)
   
    # loop through location data
    for i in data:
        loc = i.strip('\n').split(':')
	if loc[0] == 'Latitude':
	    lat = float(loc[1])
	elif loc[0] == 'Longitude':
	    long = float(loc[1])
    
    # test
    #lat = 40.742974
    #long = -73.994468 
    insta_loc = insta_api('locations', lat, long)

    # create a list of place ids
    loc_ids = []
    for i in insta_loc:
        for x in json.loads(i)["data"]:
            loc_ids.append(x["id"])

    photo_data = insta_api('locations', 'media', loc_ids)

    # loop through location photo urls
    all = {}
    for i in photo_data:
        place_photos = urllib2.urlopen(i)
	for x in place_photos:
	    if json.loads(x)["data"]:
	        for y in json.loads(x)["data"]:
		    loc_name = y["location"]["name"]
		    # create multi-dimensional dict
		    if all.has_key(loc_name):
		        all[loc_name]["image"].append(y["images"]["standard_resolution"]["url"])
			#print loc_name
			#print y["images"]["standard_resolution"]["url"]
	            else:
		        all[loc_name] = {}
		        all[loc_name]["image"] = []

            else:
	        continue
    
    # set dictionary
    all = dict(all)
 
    print lat, long

    return render_to_response('insta/location.html', {'all': all})

def loc_api(ip):
    # use the hostip api 
    api_url = "http://api.hostip.info/get_html.php?ip=%s&position=true" % ip
    loc_data = urllib2.urlopen(api_url) 

    return loc_data
