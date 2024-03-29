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
    
    # variables
    image_list = []
    comment_list = []
    comments_dict = {}
    likes_list = []
    filter_list = []
    filter_count = Counter()
    location_list = []
    caption_list = []
    tags_list = []
    dict_avg = {}

    for i in data:
        # count the number of words in the comments and caption
        for x in json.loads(i)["data"]:
            # comment count
            for y in x["comments"]["data"]:
                words = y["text"].split(' ')         
                for word in words:
                    if word in comments_dict:
                        comments_dict[word.lower()] += 1     
                    else:
                        comments_dict[word.lower()] = 1               
            # caption count
            if x["caption"] != None:
                for y in x["caption"]["text"].split():
                    if y in comments_dict:
                        comments_dict[word.lower()] += 1
                    else:
                        comments_dict[word.lower()] = 1 
            # build analysis
            comment_list.append( x["comments"]["count"])
	    likes_list.append(x["likes"]["count"])
	    filter_list.append( x["filter"])
            image_list.append(x["images"]["standard_resolution"]["url"])
	    filter_count[x["filter"]] += 1
	    location_list.append(x["location"])
	    #caption_list.append(x["caption"]["text"])
	    tags_list.append(x["tags"])

    """
    print comments_dict
    print images
    print comment_list
    print filter_list
    print filter_count
    print location_list
    print caption_list
    print tags_list
 
    print avg(float(x["comments"]["count"])}
    """

    # avg # of comments
    avg_comments = sum(comment_list)/float(len(comment_list))
    avg_likes = sum(likes_list)/float(len(likes_list))

    dict_avg['comments'] = avg_comments
    dict_avg['likes'] = avg_likes
    dict_avg['urls'] = image_list
    dict_avg['comment_dict'] = comments_dict
    #print dict_avg

    return render_to_response('insta/index.html', dict_avg)


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
    if data:
        for i in data:
            loc = i.strip('\n').split(':')
	    if loc[0] == 'Latitude':
	        if loc[1] == ' ':
		    lat = 40.728977
		else:
	            lat = float(loc[1])
	    elif loc[0] == 'Longitude':
	        if loc[1] == ' ':
                    long = -73.996288
		else: 
	            long = float(loc[1])
    else:
        # default is nyu
        lat = 40.728977
        long = -73.996288 
    
    insta_loc = insta_api('locations', lat, long)

    # create a list of place ids
    loc_ids = []
    for i in insta_loc:
        for x in json.loads(i)["data"]:
            loc_ids.append(x["id"])

    photo_data = insta_api('locations', 'media', loc_ids)

    # loop through location photo urls
    all = {}
    comment_dict = {}
    for i in photo_data:
        place_photos = urllib2.urlopen(i)
	for x in place_photos:
	    if json.loads(x)["data"]:
                # count words
	        for y in json.loads(x)["data"]:
		    loc_name = y["location"]["name"]
		    # create multi-dimensional dict
		    if all.has_key(loc_name):
		        all[loc_name]["image"].append(y["images"]["standard_resolution"]["url"])
			all[loc_name]["filter"].append(y["filter"])
			if y["caption"] != None:
			    all[loc_name]["caption"].append(y["caption"]["text"])
			if y["tags"]:
			    # list comprehension
			    all[loc_name]["tags"] = [a for a in y["tags"]]
                        if y["comments"]["count"]:
                            all[loc_name]["comment_cnt"].append(y["comments"]["count"])
                        if y["likes"]["count"]:
                            all[loc_name]["likes_cnt"].append(y["likes"]["count"])
                        # comments
                        for z in y["comments"]["data"]:
                            words = z["text"].split(' ')
                            for word in words:
                                if word in comment_dict:
                                    comment_dict[word.lower()] += 1
                                else:
                                    comment_dict[word.lower()] = 1

                                if word in all[loc_name]["comments"]:
                                    all[loc_name]["comments"][word.lower()] += 1
                                else:
                                    all[loc_name]["comments"][word.lower()] = 1
                        # caption
                        if y["caption"] != None:
                            for z in y["caption"]["text"].split():
                                if z in all[loc_name]["comments"]:
                                    all[loc_name]["comments"][z.lower()] += 1
                                else:
                                    all[loc_name]["comments"][z.lower()] = 1

		    # initialize dictionary	
	            else:
		        all[loc_name] = {}
		        all[loc_name]["image"] = []
			all[loc_name]["tags"] = []
			all[loc_name]["filter"] = []
			all[loc_name]["caption"] = []
                        all[loc_name]["comments"] = {}
                        all[loc_name]["likes_cnt"] = []
                        all[loc_name]["comment_cnt"] = []
            else:
	        continue
    
    # calculate averages
    for x in all:
        if all[x]["likes_cnt"]:
            all[x]["likes_avg"] = sum(all[x]["likes_cnt"])/len(all[x]["likes_cnt"])            
            #print all[x]["likes_avg"]
        if all[x]["comment_cnt"]:
            all[x]["comment_avg"] = sum(all[x]["comment_cnt"])/len(all[x]["comment_cnt"])
            #print all[x]["comment_avg"]


    # set dictionary
    #all["comments"] = comment_dict
    all = dict(all)
    #print comment_dict
    #print all 
    #print lat, long

    return render_to_response('insta/location.html', {'all': all})

def loc_api(ip):
    # use the hostip api 
    api_url = "http://api.hostip.info/get_html.php?ip=%s&position=true" % ip
    loc_data = urllib2.urlopen(api_url) 

    return loc_data
