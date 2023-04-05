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
#***************************************************************************
api_key = "K11YdG8ETGyEb0zrFl8Pu7mJt"
api_secret_key = "d6zHdnXysJ09pLfkJ7b35Y9PYC9NA8x9uf96lroH3KUkisBJlG"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAKKZmQEAAAAAb%2FgBpYcuZOBK%2Fh4yeKlvpDxfQV0%3DEtp7nuyUKczlYI2O65cYS1DwdYyRdyV5s47PPDluS5yYpU6REt"
access_token = "1398611273051480072-l378mYCDWn3yMthITAJKsGiCPXcPwZ"
access_token_secret = "TuKBNFUWY1CF9G5VRLIsQmWMxnvgSgN4qCLJhnAipMyWc"
#***************************************************************************

############################################################################
#   TWITTER ACCOUNT CLASS
############################################################################
class TwitterAccount:
    def __init__(self,accountName):       
        # store the data into a list
        self.allTweets = []
        # create authentication object
        auth = tweepy.OAuthHandler(api_key, api_secret_key,access_token, access_token_secret)
        # Create an API object
        api = tweepy.API(auth)
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
        with open(file_path, mode='a', newline='') as csv_file:
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
        self.tweetText = tweetText
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
#   GENERAL PROGRAM SCRIPT
############################################################################
a = TwitterAccount("devapitest4308")
#b = TwitterAccount("elonmusk")
#print(a)
print("this worked")
