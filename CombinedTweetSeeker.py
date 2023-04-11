############################################################################
#   DEPENDANCY IMPORTS AND CHECKS
############################################################################
import importlib
import subprocess
import requests
import tweepy
import csv
import datetime
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import boto3


############################################################################
#   CREATE GLOBAL TWEEPY API OBJECT
############################################################################

import tweepy
import tkinter as tk

def createTwitterAPI(apiKey, apiSecretKey, accessToken, accessTokenSecret):
    # create authentication object
    global auth 
    auth = tweepy.OAuthHandler(apiKey, apiSecretKey)
    auth.set_access_token(accessToken, accessTokenSecret)

    # Create an API object
    global api 
    api= tweepy.API(auth)

    # Test if the keys are valid
    try:
        api.verify_credentials()
        print("Authentication Successful")
        # start the main method to perform the twitter scraping
        authenticatedMain()
    except Exception as e:
        #print("Authentication Failed:", e)
        tk.messagebox.showerror("Twitter API Key Authentication Error", 
            "Authentication Failed: 401 Unauthorized, 89 - Invalid or expired token.")

############################################################################
#   AWS CLOUD SECRETS MANAGER 
############################################################################

def authenticateAWS(awsAccessKey,awsSecretKey,awsRegionName):

    def get_secrets(secret_name=''):
        try:
            if secret_name == '':
                raise Exception("Secret Name cannot be Null ")

            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                awsAccessKey_id=awsAccessKey,
                aws_secret_access_key=awsSecretKey,
                region_name=awsRegionName
            )

            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )

            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                secret = json.loads(secret)
                for key, value in secret.items():
                    os.environ[key] = value

                # Successful login
                print("Login successful.")
                return {
                    "status": 200,
                    "error": {},
                    "data": {
                        "message": True
                    }
                }
            else:
                # Failed login
                print("Login failed.")
                return {
                    "status": -1,
                    "error": {
                        "message": "Failed to retrieve secrets."
                    }
                }

        except Exception as e:
            # Failed login
            print("Login failed.")
            return {
                "status": -1,
                "error": {
                    "message": str(e)
                }
            }

    secrets_name = "TweetSeeker"
    response_secrets = get_secrets(secret_name=secrets_name)
    # Check if login was successful
    if response_secrets["status"] == 200:
        # Secrets are available
        print(os.getenv("api_key"))
        print(os.getenv("api_secret_key"))
        #print(os.getenv("bearer_token"))
        print(os.getenv("access_token"))
        print(os.getenv("access_token_secret"))
    else:
        # Secrets not available
        print("Unable to retrieve secrets.")

############################################################################
#   LOGIN/API PROGRAM OPTIONS GUI
############################################################################

def checkInputsFilled():
    if awsVar.get() and awsKey.get() and awsSecret.get() and awsRegion.get():
        loginButton.config(state='normal')
    elif (not awsVar.get() and twApiKey.get() and twApiSecretKey.get()
          and twAccessToken.get() and twAccessTokenSecret.get()):
        loginButton.config(state='normal')
    else:
        loginButton.config(state='disabled')

def enableDisableElements():
    if awsVar.get():
        enableAwsElements()
        disableTwElements()
    else:
        enableTwElements()
        disableAwsElements()
    checkInputsFilled()

def enableAwsElements():
    awsKeyLabel.config(state='normal')
    awsKeyEntry.config(state='normal')
    awsSecretLabel.config(state='normal')
    awsSecretEntry.config(state='normal')
    awsRegionLabel.config(state='normal')
    awsRegionEntry.config(state='normal')

def disableAwsElements():
    awsKeyLabel.config(state='disabled')
    awsKeyEntry.config(state='disabled')
    awsSecretLabel.config(state='disabled')
    awsSecretEntry.config(state='disabled')
    awsRegionLabel.config(state='disabled')
    awsRegionEntry.config(state='disabled')

def enableTwElements():
    twApiKeyLabel.config(state='normal')
    twApiKeyEntry.config(state='normal')
    twApiSecretKeyLabel.config(state='normal')
    twApiSecretKeyEntry.config(state='normal')
    twAccessTokenLabel.config(state='normal')
    twAccessTokenEntry.config(state='normal')
    twAccessTokenSecretLabel.config(state='normal')
    twAccessTokenSecretEntry.config(state='normal')

def disableTwElements():
    twApiKeyLabel.config(state='disabled')
    twApiKeyEntry.config(state='disabled')
    twApiSecretKeyLabel.config(state='disabled')
    twApiSecretKeyEntry.config(state='disabled')
    twAccessTokenLabel.config(state='disabled')
    twAccessTokenEntry.config(state='disabled')
    twAccessTokenSecretLabel.config(state='disabled')
    twAccessTokenSecretEntry.config(state='disabled')

def submit_login():
    if awsVar.get():
        print("AWS Key:", awsKey.get())
        print("AWS Secret:", awsSecret.get())
        print("Region:", awsRegion.get())
        authenticateAWS(awsKey.get(),awsSecret.get(),awsRegion.get())
    else:
        print("---------------------------------------")
        print("API Key:", twApiKey.get())
        print("API Secret Key:", twApiSecretKey.get())
        print("Access Token:", twAccessToken.get())
        print("Access Token Secret:", twAccessTokenSecret.get())
        print("---------------------------------------")
        createTwitterAPI(twApiKey.get(), twApiSecretKey.get(),twAccessToken.get(), twAccessTokenSecret.get())
    root.destroy()

root = tk.Tk()
root.title("TweetSeeker v1.0")

awsVar = tk.BooleanVar()
awsVar.set(True)

awsRadio = ttk.Radiobutton(root, text="AWS Cloud Login", variable=awsVar, value=True, command=enableDisableElements)
awsRadio.grid(row=0, column=0, sticky='w')

twRadio = ttk.Radiobutton(root, text="Twitter Developer's API Keys", variable=awsVar, value=False, command=enableDisableElements)
twRadio.grid(row=0, column=1, sticky='w')

awsKeyLabel = ttk.Label(root, text="AWS Key:")
awsKeyLabel.grid(row=1, column=0, sticky='e')
awsKey = tk.StringVar()
awsKeyEntry = ttk.Entry(root, textvariable=awsKey)
awsKeyEntry.grid(row=1, column=1)

awsSecretLabel = ttk.Label(root, text="AWS Secret:")
awsSecretLabel.grid(row=2, column=0, sticky='e')
awsSecret = tk.StringVar()
awsSecretEntry = ttk.Entry(root, textvariable=awsSecret)
awsSecretEntry.grid(row=2, column=1)

awsRegionLabel = ttk.Label(root, text="Region:")
awsRegionLabel.grid(row=3, column=0, sticky='e')
awsRegion = tk.StringVar()
awsRegionEntry = ttk.Entry(root, textvariable=awsRegion)
awsRegionEntry.grid(row=3, column=1)

twApiKeyLabel = ttk.Label(root, text="API Key:")
twApiKeyLabel.grid(row=4, column=0, sticky='e')
twApiKey = tk.StringVar()
twApiKeyEntry = ttk.Entry(root, textvariable=twApiKey)
twApiKeyEntry.grid(row=4, column=1)

twApiSecretKeyLabel = ttk.Label(root, text="API Secret Key:")
twApiSecretKeyLabel.grid(row=5, column=0, sticky='e')
twApiSecretKey = tk.StringVar()
twApiSecretKeyEntry = ttk.Entry(root, textvariable=twApiSecretKey)
twApiSecretKeyEntry.grid(row=5, column=1)

twAccessTokenLabel = ttk.Label(root, text="Access Token:")
twAccessTokenLabel.grid(row=6, column=0, sticky='e')
twAccessToken = tk.StringVar()
twAccessTokenEntry = ttk.Entry(root, textvariable=twAccessToken)
twAccessTokenEntry.grid(row=6, column=1)

twAccessTokenSecretLabel = ttk.Label(root, text="Access Token Secret:")
twAccessTokenSecretLabel.grid(row=7, column=0, sticky='e')
twAccessTokenSecret = tk.StringVar()
twAccessTokenSecretEntry = ttk.Entry(root, textvariable=twAccessTokenSecret)
twAccessTokenSecretEntry.grid(row=7, column=1)

loginButton = ttk.Button(root, text="Login", state='disabled', command=submit_login)
loginButton.grid(row=8, column=0, columnspan=2, pady=10)

enableDisableElements()

awsKey.trace_add("write", lambda *args: checkInputsFilled())
awsSecret.trace_add("write", lambda *args: checkInputsFilled())
awsRegion.trace_add("write", lambda *args: checkInputsFilled())
twApiKey.trace_add("write", lambda *args: checkInputsFilled())
twApiSecretKey.trace_add("write", lambda *args: checkInputsFilled())
twAccessToken.trace_add("write", lambda *args: checkInputsFilled())
twAccessTokenSecret.trace_add("write", lambda *args: checkInputsFilled())


############################################################################
#   TWITTER ACCOUNT CLASS
############################################################################
class TwitterAccount:
    def __init__(self,accountName):       
        # store the data into a list
        self.allTweets = []

        # Retrieve the user object of the specified account
        user = api.get_user(screen_name=accountName)
        user_id = user.id
        # get account details
        self.accountID = user.id
        self.accountName = user.name
        self.screenName = f"@{user.screen_name}"
        self.description = f"{user.description if (len(user.description) != 0) else None}"
        self.descriptionEntities = user.entities
        self.isVerified = user.verified
        self.followersCount = user.followers_count
        self.friendsCount = user.friends_count
        self.listedCount = user.listed_count
        self.ratio = f"{user.followers_count / user.friends_count if user.friends_count != 0 else 0:.2f}"
        self.createdAt = user.created_at
        self.timeZone = user.time_zone
        self.geoEnabled = user.geo_enabled
        self.location = f"{user.location if user.location != None else None}"
        self.profileURL = f"https://twitter.com/{user.screen_name}"
        self.profileImageURL = f"{user.profile_image_url}"
        self.hasProtectedTweets = user.protected

        for tweet in tweepy.Cursor(api.user_timeline, user_id=user_id, tweet_mode='extended').items():
            tweetID = tweet.id
            createdAt = tweet.created_at
            tweetText = tweet.full_text
            language = tweet.lang
            tweetURL = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
            favoriteCount = tweet.favorite_count
            retweetCount = tweet.retweet_count
            mentionedUsers = f"{tweet.entities['user_mentions']}"
            tweetEntities = tweet.entities
            # get the photo URL's
            tweetPhotoURLs = []
            if 'media' in tweet.entities:
                for media in tweet.entities['media']:
                    if media['type'] == 'photo':
                        tweetPhotoURLs.append(media['media_url'])
            if 'extended_entities' in tweet._json:
                for media in tweet._json['extended_entities']['media']:
                    if media['type'] == 'photo':
                        tweetPhotoURLs.append(media['media_url'])
            if len(tweetPhotoURLs) == 0:
                tweetPhotoURLs = None
            else:
                tweetPhotoURLs = list(set(tweetPhotoURLs))
            # get the video URL's
            tweetVideoURLs = []
            if 'media' in tweet.entities:
                for media in tweet.entities['media']:
                    if media['type'] == 'video':
                        variants = media['video_info']['variants']
                        video_url = max(variants, key=lambda variant: variant.get('bitrate', 0)).get('url', '')
                        tweetVideoURLs.append(video_url)
            if 'extended_entities' in tweet._json:
                for media in tweet._json['extended_entities']['media']:
                    if media['type'] == 'video':
                        variants = media['video_info']['variants']
                        video_url = max(variants, key=lambda variant: variant.get('bitrate', 0)).get('url', '')
                        tweetVideoURLs.append(video_url)
            if len(tweetVideoURLs) == 0:
                tweetVideoURLs = None
            else:
                tweetVideoURLs = list(set(tweetVideoURLs))
            #pull the URLs from the tweet text: 
            tweetURLs = []
            if 'entities' in tweet._json:
                urls = tweet._json['entities']['urls']
                for url in urls:
                    url_text = url['url']
                    if url['expanded_url']:
                        url_text = url['expanded_url']
                    tweetURLs.append(url_text)
            if len(tweetURLs) == 0:
                tweetURLs = None
            else:
                tweetURLs = list(set(tweetURLs))
            geoData = tweet.geo
            #coordinate data
            coordinates = None
            if tweet.place is not None and tweet.place.bounding_box is not None:
                coordinates = tweet.place.bounding_box.centroid
            self.allTweets.append(Tweet(tweetID,createdAt,tweetText,language,
            tweetURL,favoriteCount,
            retweetCount,mentionedUsers,
            tweetEntities,tweetPhotoURLs,
            tweetVideoURLs,tweetURLs,
            geoData,coordinates))
        #save account/tweet data into a csv file
        self.saveAccountDataAsCSV()
        self.saveTweetDataAsCSV()

    def getAccountID(self):
        return self.accountID

    def getAccountName(self):
        return self.accountName

    def getScreenName(self):
        return self.screenName

    def getDescription(self):
        return self.description

    def getDescriptionEntities(self):
        return self.descriptionEntities

    def getIsVerified(self):
        return self.isVerified

    def getFollowersCount(self):
        return self.followersCount

    def getFriendsCount(self):
        return self.friendsCount

    def getListedCount(self):
        return self.listedCount

    def getRatio(self):
        return self.ratio

    def getCreatedAt(self):
        return self.createdAt

    def getTimeZone(self):
        return self.timeZone

    def getGeoEnabled(self):
        return self.geoEnabled

    def getLocation(self):
        return self.location

    def getProfileURL(self):
        return self.profileURL

    def getProfileImageURL(self):
        return self.profileImageURL

    def getHasProtectedTweets(self):
        return self.hasProtectedTweets

    def getAllAccountData(self):
        result = []
        labels = ["accountID","accountName","screenName","description",
        "descriptionEntities","isVerified","followersCount","friendsCount",
        "listedCount","ratio","createdAt","timeZone","geoEnabled","location",
        "profileURL","profileImageURL","hasProtectedTweets"]
        accountData = [self.accountID,self.accountName,self.screenName,
        self.description,self.descriptionEntities,self.isVerified,self.followersCount,
        self.friendsCount,self.listedCount,self.ratio,self.createdAt,self.timeZone,
        self.geoEnabled,self.location,self.profileURL,self.profileImageURL,
        self.hasProtectedTweets] 
        
        for label, variable in zip(labels, accountData):
            result.append([label, variable])
        return result       

    def saveAccountDataAsCSV(self):
        dataToSave = self.getAllAccountData()
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, f"{self.screenName}_account_data.csv")
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(dataToSave)

    def saveTweetDataAsCSV(self):
        current_dir = os.getcwd()
        # append the file name to the current directory
        file_path = os.path.join(current_dir, f"{self.screenName}_tweet_data.csv")
        # open the csv file in append mode

        #BUG FIX: utf-8 was included to fix glitches regarding emoji characters
        with open(file_path, mode='a', newline='',encoding='utf-8') as csv_file:
            # create a csv writer object
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            # write the variables as a new row in the csv file
            writer.writerow(["tweetID","createdAt","tweetText","language","tweetURL",
            "favoriteCount","retweetCount","mentionedUsers","tweetEntities",
            "tweetPhotoURLs","tweetVideoURLs","tweetURLs","geoData","coordinates"])

            for tweet in self.allTweets:
                writer.writerow([tweet.tweetID,tweet.createdAt,
                tweet.tweetText,tweet.language,tweet.tweetURL,
                tweet.favoriteCount,tweet.retweetCount,tweet.mentionedUsers,tweet.tweetEntities,
                tweet.tweetPhotoURLs,tweet.tweetVideoURLs,tweet.tweetURLs,tweet.geoData,tweet.coordinates])               

    # to string method
    def __str__(self):
        result = f"========================================================================================\n"
        result += "{:<32} {}\n".format("","General Account Data:")
        result += f"========================================================================================\n"
        result += "{:<28}: {}\n".format("Account ID", self.accountID)
        result += "{:<28}: {}\n".format("Account UserName", self.accountName)
        result += "{:<28}: {}\n".format("Account ScreenName", self.screenName)
        result += "{:<28}: {}\n".format("Account Description", self.description)
        result += "{:<28}: {}\n".format("Account Description Entities", self.descriptionEntities)
        result += "{:<28}: {}\n".format("Is Verified", self.isVerified)
        result += "{:<28}: {}\n".format("Followers Count", self.followersCount)
        result += "{:<28}: {}\n".format("Friends Count", self.friendsCount)
        result += "{:<28}: {}\n".format("Listed Count", self.listedCount)
        result += "{:<28}: {}\n".format("Account Ratio", self.ratio)
        result += "{:<28}: {}\n".format("Account Created At", self.createdAt)
        result += "{:<28}: {}\n".format("Account Time zone", self.timeZone)
        result += "{:<28}: {}\n".format("Account Geo Enabled", self.geoEnabled)
        result += "{:<28}: {}\n".format("Account Location", self.location)
        result += "{:<28}: {}\n".format("Profile URL", self.profileURL)
        result += "{:<28}: {}\n".format("Profile Image URL", self.profileImageURL)
        result += "{:<28}: {}\n".format("Account has Protected Tweets", self.hasProtectedTweets)
        result += f"\n"
        result += f"**************************************************************************************\n"
        result += "{:<16} {}\n".format("",f"All Tweet Data from {self.screenName}")
        result += f"**************************************************************************************\n"
        for x in range(0,len(self.allTweets)):
            result += str(self.allTweets[x])
            result += f"--------------------------------------------------------------------------------------\n"
        return result
    

############################################################################
#   TWEET CLASS
############################################################################
class Tweet:
    def __init__(self,
        tweetID,createdAt,tweetText,language,tweetURL,favoriteCount,retweetCount,mentionedUsers,
        tweetEntities,tweetPhotoURLs,tweetVideoURLs,tweetURLs,geoData,coordinates):
        # set the internal variables
        self.tweetID = tweetID
        self.createdAt = createdAt
        #BUG FIX: remove newlines from tweet text to reduce issues with .csv parsing
        self.tweetText = tweetText.replace('\n', '')
        self.language = language
        self.tweetURL = tweetURL
        self.favoriteCount = favoriteCount
        self.retweetCount = retweetCount
        self.mentionedUsers = mentionedUsers
        self.tweetEntities = tweetEntities
        self.tweetPhotoURLs = tweetPhotoURLs
        self.tweetVideoURLs = tweetVideoURLs
        self.tweetURLs = tweetURLs
        self.geoData = geoData
        self.coordinates = coordinates

    #getter methods
    def getTweetID(self):
        return self.tweetID

    def getTweetCreatedAt(self):
        return self.createdAt

    def getTweetText(self):
        return self.tweetText

    def getTweetLanguage(self):
        return self.language

    def getTweetURL(self):
        return self.tweetURL

    def getTweetFavoriteCount(self):
        return self.favoriteCount

    def getTweetRetweetCount(self):
        return self.retweetCount

    def getTweetMentionedUsers(self):
        return self.mentionedUsers

    def getTweetEntities(self):
        return self.tweetEntities

    def getTweetPhotoURLs(self):
        return self.tweetPhotoURLs

    def getTweetVideoURLs(self):
        return self.tweetVideoURLs

    def getTweetURLs(self):
        return self.tweetURLs

    def getTweetGeoData(self):
        return self.geoData

    def getTweetCoordinates(self):
        return self.coordinates

    def getAllTweetData(self):
        labels = ["tweetID","createdAt","tweetText","language","tweetURL",
            "favoriteCount","retweetCount","mentionedUsers","tweetEntities",
            "tweetPhotoURLs","tweetVideoURLs","tweetURLs","geoData","coordinates"] 
        tweetData = [self.tweetID,self.createdAt,self.tweetText,self.language,
            self.tweetURL,self.favoriteCount,self.retweetCount,self.mentionedUsers,
            self.tweetEntities,self.tweetPhotoURLs,self.tweetVideoURLs,self.tweetURLs,
            self.geoData,self.coordinates]
        return tweetData

    def __str__(self):
        result = "{:<16}: {}\n".format("Tweet ID", self.tweetID)
        result += "{:<16}: {}\n".format("Created At", self.createdAt)
        result += "{:<16}: {}\n".format("Tweet Text", self.tweetText)
        result += "{:<16}: {}\n".format("Language", self.language)
        result += "{:<16}: {}\n".format("Tweet URL", self.tweetURL)
        result += "{:<16}: {}\n".format("Favorite Count", self.favoriteCount)
        result += "{:<16}: {}\n".format("Retweet Count", self.retweetCount)
        result += "{:<16}: {}\n".format("Mentioned Users", self.mentionedUsers)
        result += "{:<16}: {}\n".format("Tweet Entities", self.tweetEntities)
        result += "{:<16}: {}\n".format("Tweet Photo URLs", self.tweetPhotoURLs)
        result += "{:<16}: {}\n".format("Tweet Video URLs", self.tweetVideoURLs)
        result += "{:<16}: {}\n".format("Tweet URLs", self.tweetURLs)
        result += "{:<16}: {}\n".format("Geo Data", self.geoData)
        result += "{:<16}: {}\n".format("Coordinates", self.coordinates)
        return result
    

############################################################################
#   MAIN PROGRAM
############################################################################

def authenticatedMain():
    pass

def main():
    # Start the primary GUI code 
    root.mainloop()

if __name__ == "__main__":
    main()