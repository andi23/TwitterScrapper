# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 20:13:56 2018

@author: andi3
"""

import numpy as np
import pandas as pd
import tweepy
import matplotlib.pyplot as plt
import pymongo
import ipywidgets as wgt
from IPython.display import display
from sklearn.feature_extraction.text import CountVectorizer
import re
from datetime import datetime

from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')

## Authentication key
api_key = "6EoSQYVzWJxAVSIfjFbeVz0KD" # <---- Add your API Key
api_secret = "cajemYKbFzU1eVaTGHBhwOvCxNSfr5ioB1pJQgZBX8mhgQ5PNg" # <---- Add your API Secret
access_token = "942986127941648386-jK30WoZjCVIQO8DwX0kQuIY2LouObhV" # <---- Add your access token
access_token_secret = "7wpNov5hRZdcGYYg2sF2mDcakfXafsUNQOOEpERWTI4ES" # <---- Add your access token secret

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

col = pymongo.MongoClient()["tweets"]["StreamingTutorial"]
col.count()

class MyStreamListener(tweepy.StreamListener):
    
    counter = 0
    
    def __init__(self, max_tweets=50, *args, **kwargs):
        super().__init__()
        self.counter = 0
        self.max_tweets = 10
    
    def on_connect(self):
        self.counter = 0
        self.start_time = datetime.now()
    
    def on_status(self, status):
        # Increment counter
        self.counter += 1
        
        # Store tweet to MongoDB
        col.insert_one(status._json)
        
        
        if self.counter % 1 == 0:
            print(self.counter)
            value = int(100.00 * self.counter / self.max_tweets)
            mining_time = datetime.now() - self.start_time
            progress_bar.value = value
            html_value = """<span class="label label-primary">Tweets/Sec: %.1f</span>""" % (self.counter / max([1,mining_time.seconds]))
            html_value += """ <span class="label label-success">Progress: %.1f%%</span>""" % (self.counter / self.max_tweets * 100.0)
            html_value += """ <span class="label label-info">ETA: %.1f Sec</span>""" % ((self.max_tweets - self.counter) / (self.counter / max([1,mining_time.seconds])))
            wgt_status.value = html_value
            #print("%s/%s" % (self.counter, self.max_tweets))
            if self.counter >= self.max_tweets:
                myStream.disconnect()
                print("Finished")
                print("Total Mining Time: %s" % (mining_time))
                print("Tweets/Sec: %.1f" % (self.max_tweets / mining_time.seconds))
                progress_bar.value = 0
                
    
myStreamListener = MyStreamListener(max_tweets=100)
myStream = tweepy.streaming.Stream(auth = api.auth, listener=myStreamListener)

keywords = ["Jupyter",
            "Python",
            "Data Mining",
            "Machine Learning",
            "Data Science",
            "Big Data",
            "DataMining",
            "MachineLearning",
            "DataScience",
            "BigData",
            "IoT",
            "#R",
           ]

# Visualize a progress bar to track progress
progress_bar = wgt.IntProgress(value=0)
display(progress_bar)
wgt_status = wgt.HTML(value="""<span class="label label-primary">Tweets/Sec: 0.0</span>""")
display(wgt_status)

box =  [-0.510375,	51.286758,0.334015,51.691875] #london
# Start a filter with an error counter of 20
for error_counter in range(20):
    try:
        myStream.filter(track=keywords, languages = ["en"])
        print("Tweets collected: %s" % myStream.listener.counter)
        print("Total tweets in collection: %s" % col.count())
        break
    except:
        print("ERROR# %s" % (error_counter + 1))
              
col.find_one()

dataset = [{"created_at": item["created_at"],
            "text": item["text"],
            "user": "@%s" % item["user"]["screen_name"],
            'Coordinates': item["coordinates"],
            "source": item["source"],
           } for item in col.find()]

dataset = pd.DataFrame(dataset)
dataset

cv = CountVectorizer()
count_matrix = cv.fit_transform(dataset.text)

word_count = pd.DataFrame(cv.get_feature_names(), columns=["word"])
word_count["count"] = count_matrix.sum(axis=0).tolist()[0]
word_count = word_count.sort_values("count", ascending=False).reset_index(drop=True)
word_count[:50]
dataset.to_csv('out.tsv', sep='\t')

testset = pd.read_csv('out.tsv', delimiter = '\t', quoting = 3)
