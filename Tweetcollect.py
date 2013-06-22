#!/usr/bin/python
#
# Author: Antitree
# Description: Example of using the new Twitter 1.1 API to 
#  collect all the tweets from a user. 
#
# Derived from tsileo
# https://gist.github.com/tsileo/4637864/raw/9ea056ffbe5bb88705e95b786332ae4c0fd7554c/mytweets.py
#

import requests
import sqlite3, sys
from requests_oauthlib import OAuth1

# Go to https://dev.twitter.com/apps and create a new application
# Paste in your information here
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

#Fill this in with the keys you receive after the first run
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""   
 
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""


################################
if len(sys.argv) is 2:  
    SCREENNAME = sys.argv[1]
else: SCREENNAME = "rossja" 

AUTH = ''
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
 
def setup_oauth():
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
 
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]
    
    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url
    
    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)
 
    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]
 
    return token, secret
 
 
def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth


def get_all_tweets(screenname, auth=AUTH):
    
    count = 200 #Max for the 1.1 API is 200 per request
    tweets = []
    
    #The max_id value sets from where to start collecting tweets.
    # e.g. 1234 means that you would get tweets older than 1234
    maxstr = "&max_id="
    lastid = ""
    maxid = ""  

    while True:
        # Call the API and collect the response as a JSON response
        r = requests.get(
            url="https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&include_rts=1&count=%s%s" 
            % (screenname, count, maxid, ), auth=AUTH, ).json()
        tweets += r
        lastid = r[len(r)-1]["id"]
        maxid = maxstr+str(lastid)      # update the Max_Id value
        
        if len(r) is 1:                 # You found all the tweets
            break
        
        print("Collecting next set of tweets starting at %s " % lastid)
    
    print("Collected %s tweets from %s" % (len(tweets), SCREENNAME))
    return tweets

def store_tweets(tweets):
    con = sqlite3.connect('tweet.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS '+ SCREENNAME +'  (id text, tweet text, date text)')
    for tweet in tweets:
        cur.execute('INSERT OR REPLACE INTO '+ SCREENNAME +' VALUES(?,?,?)', (tweet['id'], tweet['text'], tweet['created_at']))
    cur.close()
    con.commit()
    
    
if __name__ == "__main__":
    #Setup OAuth if we haven't already
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        AUTH = get_oauth()
        tweets = get_all_tweets("antitree")
        store_tweets(tweets)