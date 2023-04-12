"""
****************************************************************************
Program:            TweetSeeker
Written by:         Austin A. Daigle
Date:               4/11/2023
Version:            1.0
Build:              Stable Alpha
Authentication:     AWS Cloud Secrets Managemet or Twitter API Keys via GUI
Dependancies:       See below (also run the dependancy installer script)
Assignment:         Team Semester Project for CSCI 4308
Required Function:  Cloud Computing (AWS Secrets Manager)
****************************************************************************
"""
# Update the header above as changes/features are added

############################################################################
#   DEPENDANCY IMPORTS
############################################################################
import tkinter as tk
from tkinter import messagebox
import importlib
import subprocess
import requests
import tweepy
import csv
import datetime
import os
import json
import boto3

############################################################################
#   CREATE GLOBAL TWEEPY API OBJECT
############################################################################

# this method creates and authenticates Twitter API objects using the Tweetpy library
def createTwitterAPI(apiKey, apiSecretKey, accessToken, accessTokenSecret):
    # create global authentication object
    # these objects are global so that once they are created they can be used in any location/method/level
    global auth 
    auth = tweepy.OAuthHandler(apiKey, apiSecretKey)
    auth.set_access_token(accessToken, accessTokenSecret)
    # Create an Twitter API object
    global api 
    api= tweepy.API(auth)
    # Test if the API keys are valid
    try:
        api.verify_credentials()
        tk.messagebox.showinfo("Success", "Twitter Keys Successfully Authenticated.")
        # start the main method to perform the twitter scraping
        authenticatedMain()
    except Exception as e:
        #print("Authentication Failed:", e)
        tk.messagebox.showerror("Twitter API Authentication Error", 
            f"Authentication Failed!\nReason(s):\n{e}")

############################################################################
#   AWS CLOUD SECRETS MANAGER 
############################################################################

# this method authenticates the user access id and access key secret for AWS
# Cloud Secrets Manager
def authenticateAWS(awsAccessKey,awsSecretKey,awsRegionName):
    # this method authenticate AWS details and pull Twitter API Keys details 
    # for the creation of a Tweepy object.
    def getSecrets(secret_name=''):
        # try the process with the given details
        try:
            # if there is no secret name, raise an exception
            # this error should not be a problem since the AWS
            # secret manager name "TweekSeeker" is hardcoded
            # into the program
            if secret_name == '':
                raise Exception("Secret Name cannot be Null ")
            # create and run AWS session objects with the given details
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                aws_access_key_id=awsAccessKey,
                aws_secret_access_key=awsSecretKey,
                region_name=awsRegionName
            )
            # create a secret value response object
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            # load the secret value object with the environment check
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                secret = json.loads(secret)
                for key, value in secret.items():
                    os.environ[key] = value
                # Successful login
                return {
                    "status": 200,
                    "error": {},
                    "data": {
                        "message": True
                    }
                }
            else:
                # Failed login
                return {
                    "status": -1,
                    "error": {
                        "message": "Failed to retrieve secrets."
                    }
                }  
        # throw an exception for failed login cases
        except Exception as e:
            # Failed login
            return {
                "status": -1,
                "error": {
                    "message": str(e)
                }
            }
    # create secret name contents
    secrets_name = "TweetSeeker"
    response_secrets = getSecrets(secret_name=secrets_name)
    # Check if login was successful
    if response_secrets["status"] == 200:
        # Secrets are available
        tk.messagebox.showinfo("Success", "AWS Details Authenticated Successfully.")
        # Create API object
        # Authenticate the twitter API key data
        createTwitterAPI(os.getenv("api_key"), os.getenv("api_secret_key"),
            os.getenv("access_token"), os.getenv("access_token_secret"))
    else:
        # Secrets not available, create API error message GUI       
        tk.messagebox.showerror("AWS Authentication Failure", 
            "AWS Details Failed To Authenticate. Please Check all details and retry")

############################################################################
#   LOGIN/API PROGRAM OPTIONS GUI
############################################################################

# this method checks the login button if the fields in the GUI 
# are not filled.
def checkInputsFilled():
    # aws option is selected, perform the check
    if awsVar.get() and awsKey.get() and awsSecret.get() and awsRegion.get():
        loginButton.config(state='normal')
    # twitter option is selected, perform the check
    elif (not awsVar.get() and twApiKey.get() and twApiSecretKey.get()
          and twAccessToken.get() and twAccessTokenSecret.get()):
        loginButton.config(state='normal')
    # disable otherwise
    else:
        loginButton.config(state='disabled')
# button enabled/disables elements as required from the GUI
# inputs for the two startup options
def enableDisableElements():
    # if the AWS option is selected
    if awsVar.get():
        enableAwsElements()
        disableTwElements()
    # if the twitter option is selected
    else:
        enableTwElements()
        disableAwsElements()
    checkInputsFilled()
# enabled ASW elements 
def enableAwsElements():
    awsKeyLabel.config(state='normal')
    awsKeyEntry.config(state='normal')
    awsSecretLabel.config(state='normal')
    awsSecretEntry.config(state='normal')
    awsRegionLabel.config(state='normal')
    awsRegionEntry.config(state='normal')
# disable AWS elements 
def disableAwsElements():
    awsKeyLabel.config(state='disabled')
    awsKeyEntry.config(state='disabled')
    awsSecretLabel.config(state='disabled')
    awsSecretEntry.config(state='disabled')
    awsRegionLabel.config(state='disabled')
    awsRegionEntry.config(state='disabled')
# disable Twitter elements
def enableTwElements():
    twApiKeyLabel.config(state='normal')
    twApiKeyEntry.config(state='normal')
    twApiSecretKeyLabel.config(state='normal')
    twApiSecretKeyEntry.config(state='normal')
    twAccessTokenLabel.config(state='normal')
    twAccessTokenEntry.config(state='normal')
    twAccessTokenSecretLabel.config(state='normal')
    twAccessTokenSecretEntry.config(state='normal')
# disable Twitter elements
def disableTwElements():
    twApiKeyLabel.config(state='disabled')
    twApiKeyEntry.config(state='disabled')
    twApiSecretKeyLabel.config(state='disabled')
    twApiSecretKeyEntry.config(state='disabled')
    twAccessTokenLabel.config(state='disabled')
    twAccessTokenEntry.config(state='disabled')
    twAccessTokenSecretLabel.config(state='disabled')
    twAccessTokenSecretEntry.config(state='disabled')
# login button method
def submit_login():
    # if AWS option has been selected then close the 
    # lancher GUI and authenticate the AWS details
    #       the order of progression for AWS is: 
    #       GUI -> Authenticate AWS -> Authenticate Twitter Keys -> Run program
    if awsVar.get():
        # close the main login GUI
        root.destroy()
        # authenticate the AWS information
        authenticateAWS(awsKey.get(),awsSecret.get(),awsRegion.get())
    # if Twitter Key option has been selected then close the 
    # lancher GUI and authenticate the AWS details
    #       the order of progression for Twitter API is: 
    #       GUI -> Authenticate Twitter Keys -> Run program
    else:
        # close the main login GUI
        root.destroy()
        # authenticate the twitter API keys
        createTwitterAPI(twApiKey.get(), twApiSecretKey.get(),twAccessToken.get(), twAccessTokenSecret.get())
# create the main GUI grame using the tkinter library
root = tk.Tk()
# set the title of the login GUI as "TweetSeeker v1.0"
root.title("TweetSeeker v1.0")
# Set root window not resizable
root.resizable(False, False)
# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Calculate x and y coordinates to center the window
x = int((screen_width - root.winfo_reqwidth()) / 2)
y = int((screen_height - root.winfo_reqheight()) / 2)
# Set the position of the window to the center of the screen
root.geometry("+{}+{}".format(x, y))
# set the visibility to true
awsVar = tk.BooleanVar()
awsVar.set(True)
# create the AWS Cloud login radio button
awsRadio = tk.Radiobutton(root, text="AWS Cloud Login", variable=awsVar, value=True, command=enableDisableElements)
awsRadio.grid(row=0, column=0, sticky='w')
# create the Twitter Key Login radio button
twRadio = tk.Radiobutton(root, text="Twitter Developer's API Keys", variable=awsVar, value=False, command=enableDisableElements)
twRadio.grid(row=0, column=1, sticky='w')
# create the AWS key label field
awsKeyLabel = tk.Label(root, text="AWS Key ID:")
awsKeyLabel.grid(row=1, column=0, sticky='e')
awsKey = tk.StringVar()
awsKeyEntry = tk.Entry(root, textvariable=awsKey)
awsKeyEntry.grid(row=1, column=1)
# create the AWS Key Secret label and field
awsSecretLabel = tk.Label(root, text="AWS Key Secret:")
awsSecretLabel.grid(row=2, column=0, sticky='e')
awsSecret = tk.StringVar()
awsSecretEntry = tk.Entry(root, textvariable=awsSecret,show="•")
awsSecretEntry.grid(row=2, column=1)
# create the AWS region label and field 
awsRegionLabel = tk.Label(root, text="Region:")
awsRegionLabel.grid(row=3, column=0, sticky='e')
awsRegion = tk.StringVar()
awsRegionEntry = tk.Entry(root, textvariable=awsRegion)
awsRegionEntry.grid(row=3, column=1)
#this is the default region set for the project
# change this to change the the default text
awsRegion.set("us-east-2")
# create the twitter key label and field
twApiKeyLabel = tk.Label(root, text="API Key:")
twApiKeyLabel.grid(row=4, column=0, sticky='e')
twApiKey = tk.StringVar()
twApiKeyEntry = tk.Entry(root, textvariable=twApiKey)
twApiKeyEntry.grid(row=4, column=1)
# create the twitter key secret label and field
twApiSecretKeyLabel = tk.Label(root, text="API Key Secret:")
twApiSecretKeyLabel.grid(row=5, column=0, sticky='e')
twApiSecretKey = tk.StringVar()
twApiSecretKeyEntry = tk.Entry(root, textvariable=twApiSecretKey,show="•")
twApiSecretKeyEntry.grid(row=5, column=1)
# create the twitter access token label and field
twAccessTokenLabel = tk.Label(root, text="Access Token:")
twAccessTokenLabel.grid(row=6, column=0, sticky='e')
twAccessToken = tk.StringVar()
twAccessTokenEntry = tk.Entry(root, textvariable=twAccessToken)
twAccessTokenEntry.grid(row=6, column=1)
# create the twitter token secret label
twAccessTokenSecretLabel = tk.Label(root, text="Access Token Secret:")
twAccessTokenSecretLabel.grid(row=7, column=0, sticky='e')
twAccessTokenSecret = tk.StringVar()
twAccessTokenSecretEntry = tk.Entry(root, textvariable=twAccessTokenSecret,show="•")
twAccessTokenSecretEntry.grid(row=7, column=1)
# create the login button
loginButton = tk.Button(root, text="Login", state='disabled', command=submit_login)
loginButton.grid(row=8, column=0, columnspan=2, pady=10)
# update the element that need to be enabled/disabled
enableDisableElements()
# compile the gui element and traces together
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
# this class store the account data of a given twitter account
# and all of the tweet objects as well
class TwitterAccount:
    # default constructor for a twitter account object
    def __init__(self,accountName):       
        """
        object structure: basic explanation
        the TwitterAccount object store all of the account
        data as internal fields and the tweet data is stored
        as a list containing all of the data

        Twitter Account Object
            + account_data
            + allTweets
                + [tweet1]
                + [tweet2]
                +   ...
                + [tweetN]
        """        
        # store the data into a list
        # all tweets are stored as a list with fields/sublists and
        # each tweet a list element inside of self.allTweets
        self.allTweets = []
        # Retrieve the user object of the specified account
        user = api.get_user(screen_name=accountName)
        user_id = user.id
        # get account details
        # these details are pretty self-descriptive
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
        # for every tweet in the given twitter account
        for tweet in tweepy.Cursor(api.user_timeline, user_id=user_id, tweet_mode='extended').items():
            # internal fields for tweet data fields (these are also self explanatory)
            tweetID = tweet.id
            createdAt = tweet.created_at
            tweetText = tweet.full_text
            language = tweet.lang
            tweetURL = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
            favoriteCount = tweet.favorite_count
            retweetCount = tweet.retweet_count
            mentionedUsers = f"{tweet.entities['user_mentions']}"
            tweetEntities = tweet.entities
            # get all photo photo URL's and return it as a list
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
            # get all photo video URL's and return it as a list
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
            #pull all the URLs extracted from the tweet text: 
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
            # get the geo data from the tweet
            geoData = tweet.geo
            # get the coordinate data
            coordinates = None
            if tweet.place is not None and tweet.place.bounding_box is not None:
                coordinates = tweet.place.bounding_box.centroid
            # Using the fields above, take that data and create a Tweet Object 
            # and add that to the allTweet list
            self.allTweets.append(Tweet(tweetID,createdAt,tweetText,language,
                tweetURL,favoriteCount,
                retweetCount,mentionedUsers,
                tweetEntities,tweetPhotoURLs,
                tweetVideoURLs,tweetURLs,
                geoData,coordinates))
        # End all all tweets for loop
        #save account/tweet data into a csv file
        self.saveAccountDataAsCSV()
        self.saveTweetDataAsCSV()
    # getter method for accountId
    def getAccountID(self):
        return self.accountID
    # getter method for accountName
    def getAccountName(self):
        return self.accountName
    # getter method for screenName
    def getScreenName(self):
        return self.screenName
    # getter method for description
    def getDescription(self):
        return self.description
    # getter method for descriptionEntities
    def getDescriptionEntities(self):
        return self.descriptionEntities
    # getter method for isVerfied
    def getIsVerified(self):
        return self.isVerified
    # getter method for followerCount
    def getFollowersCount(self):
        return self.followersCount
    # getter method for friendsCount
    def getFriendsCount(self):
        return self.friendsCount
    # getter method for listedCount
    def getListedCount(self):
        return self.listedCount
    # getter method for ratio
    def getRatio(self):
        return self.ratio
    # getter method for createAt
    def getCreatedAt(self):
        return self.createdAt
    # getter method for timezone
    def getTimeZone(self):
        return self.timeZone
    # getter method for geoEnabled
    def getGeoEnabled(self):
        return self.geoEnabled
    # getter method for location
    def getLocation(self):
        return self.location
    # getter method for profileURL
    def getProfileURL(self):
        return self.profileURL
    # getter method for profileImageURL
    def getProfileImageURL(self):
        return self.profileImageURL
    # getter method for hasProtectedTweets    
    def getHasProtectedTweets(self):
        return self.hasProtectedTweets
    # getter method for all of the account data return in list format seen below
    # this is useful for writing data or pulling all of the data as a "slice"
    # for the purposes of file writing or analytical methods
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
        # merge the corresponding label to the corresponding account data field
        for label, variable in zip(labels, accountData):
            result.append([label, variable])
        # return zipped result
        return result       

    # this method take all of the account data and saves it as as 
    # a CSV file
    def saveAccountDataAsCSV(self):
        # get all account data
        dataToSave = self.getAllAccountData()
        # get current working directory
        current_dir = os.getcwd()
        # create a file path object and create a .csv file with the account
        # name as the file prefix and the "_account_data.csv" as the sufix.
        file_path = os.path.join(current_dir, f"{self.screenName}_account_data.csv")
        with open(file_path, 'w', newline='') as file:
            # for every line, write to the file
            writer = csv.writer(file)
            writer.writerows(dataToSave)

    # save all of the tweet data as a .csv file
    def saveTweetDataAsCSV(self):
        current_dir = os.getcwd()
        # append the file name to the current directory
        file_path = os.path.join(current_dir, f"{self.screenName}_tweet_data.csv")
        # open the csv file in append mode
        #BUG FIX: utf-8 was included to fix glitches regarding emoji characters
        with open(file_path, mode='a', newline='',encoding='utf-8') as csv_file:
            # create a csv writer object
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            # write the variable/object name header as the first line in the 
            # filename.
            writer.writerow(["tweetID","createdAt","tweetText","language","tweetURL",
            "favoriteCount","retweetCount","mentionedUsers","tweetEntities",
            "tweetPhotoURLs","tweetVideoURLs","tweetURLs","geoData","coordinates"])
            # for every tweet in the allTweets list, take that tweet
            # data and convert it into a comma separated value line to
            # be written to the file
            for tweet in self.allTweets:
                writer.writerow([tweet.tweetID,tweet.createdAt,
                tweet.tweetText,tweet.language,tweet.tweetURL,
                tweet.favoriteCount,tweet.retweetCount,tweet.mentionedUsers,tweet.tweetEntities,
                tweet.tweetPhotoURLs,tweet.tweetVideoURLs,tweet.tweetURLs,tweet.geoData,tweet.coordinates])               

    # to string method (prints the account info first and then all of the tweet data)
    # (this is very useful for debugging)
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
        # for every tweet print the tweet
        for x in range(0,len(self.allTweets)):
            result += str(self.allTweets[x])
            result += f"--------------------------------------------------------------------------------------\n"
        return result
    
############################################################################
#   TWEET CLASS
############################################################################
# this class store the tweet data of a tweet
class Tweet:
    def __init__(self,
        tweetID,createdAt,tweetText,language,tweetURL,favoriteCount,retweetCount,mentionedUsers,
        tweetEntities,tweetPhotoURLs,tweetVideoURLs,tweetURLs,geoData,coordinates):
        # These are all of the fields from the data extracted from tweets (self explanatory)
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
    # this is a getter method for tweetID
    def getTweetID(self):
        return self.tweetID
    # this is a getter method for createdAt
    def getTweetCreatedAt(self):
        return self.createdAt
    # this is a getter method for tweetText
    def getTweetText(self):
        return self.tweetText
    # this is a getter method for language
    def getTweetLanguage(self):
        return self.language
    # this is a getter method for tweetURL
    def getTweetURL(self):
        return self.tweetURL
    # this is a getter method for favoriteCount
    def getTweetFavoriteCount(self):
        return self.favoriteCount
    # this is a getter method for retweetCount
    def getTweetRetweetCount(self):
        return self.retweetCount
    # this is a getter method for mentionedUser
    def getTweetMentionedUsers(self):
        return self.mentionedUsers
    # this is a getter method for tweetEntities
    def getTweetEntities(self):
        return self.tweetEntities
    # this is a getter method for tweetPhotoURLs
    def getTweetPhotoURLs(self):
        return self.tweetPhotoURLs
    # this is a getter method for tweetVideoURLs
    def getTweetVideoURLs(self):
        return self.tweetVideoURLs
    # this is a getter method for tweetURLs
    def getTweetURLs(self):
        return self.tweetURLs
    # this is a getter method for geoData
    def getTweetGeoData(self):
        return self.geoData
    # this is a getter method for coordinates
    def getTweetCoordinates(self):
        return self.coordinates
    # this method returns all of the data of the tweet object as a list
    def getAllTweetData(self):
        labels = ["tweetID","createdAt","tweetText","language","tweetURL",
            "favoriteCount","retweetCount","mentionedUsers","tweetEntities",
            "tweetPhotoURLs","tweetVideoURLs","tweetURLs","geoData","coordinates"] 
        tweetData = [self.tweetID,self.createdAt,self.tweetText,self.language,
            self.tweetURL,self.favoriteCount,self.retweetCount,self.mentionedUsers,
            self.tweetEntities,self.tweetPhotoURLs,self.tweetVideoURLs,self.tweetURLs,
            self.geoData,self.coordinates]
        return tweetData
    # this is a tostring method
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

# this is the actual "main method" to run the Twitter Scrapping program.
# this method is called after the Twitter API key are validated and the 
# proper API objects are created globally, this method is structured
# to ensure that all dependancies, keys, authentication, and subroutines
# are properly handled before the actual TweetSeeker GUI/program is run.
def authenticatedMain():
    # SAMPLE CODE
    # failing to put this process inside of a try/except block 
    # can lead to authentication/Tweepy API errors/unstable code
    try:
        sampleAccount = TwitterAccount("devapitest4308")
        # the print statement is only here for developement/debugging purposes
        # the program will not print anything in the end since all of you are
        # building a graphical user interface to interact with.
        print(sampleAccount)
        print("done")
    except Exception as e:
        tk.messagebox.showerror("Twitter Search Failure", 
            f"Twitter API Error!\nReason(s):\n{e}")
    # END of sample code

    # WRITE YOUR CODE HERE
    #**************************************************************************
    #TODO Write a professional GUI for the TweetSeeker scrapping interface
    #TODO Write a method(s)/class(es)/data structures to perform the analytics
    #           on the twitter account data and analytics on all of the tweets
    #TODO Write/Integrate a GUI to display all of the analytics/data found from 
    #           the account/all tweets
    #**************************************************************************

    # END of authenticatedMain()


"""
This is the main method that auto-start the program authenticator/
launch options GUI. This method, while not technically required 
but is included to ensure the proper "chain of command" on how 
the program executes structure.

Program Call Structure: 
main method -> authentication GUI -> AWS/API Authentication -> authenticatedMain() (actual program)
"""
if __name__ == "__main__":
    #DO NOT modify this code
    #main()
    root.mainloop()