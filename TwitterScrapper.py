import requests
import tweepy
#****************************************************************
api_key = "K11YdG8ETGyEb0zrFl8Pu7mJt"
api_secret_key = "d6zHdnXysJ09pLfkJ7b35Y9PYC9NA8x9uf96lroH3KUkisBJlG"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAKKZmQEAAAAAb%2FgBpYcuZOBK%2Fh4yeKlvpDxfQV0%3DEtp7nuyUKczlYI2O65cYS1DwdYyRdyV5s47PPDluS5yYpU6REt"
access_token = "1398611273051480072-l378mYCDWn3yMthITAJKsGiCPXcPwZ"
access_token_secret = "TuKBNFUWY1CF9G5VRLIsQmWMxnvgSgN4qCLJhnAipMyWc"
#****************************************************************


###################################################

def scrapTwitterAccount(accountName,
        api_key, 
        api_secret_key,
        access_token, 
        access_token_secret):

    auth = tweepy.OAuthHandler(
        api_key, 
        api_secret_key,
        access_token, 
        access_token_secret
    )
    
    # Create an API object
    api = tweepy.API(auth)

    # Retrieve the user object of the specified account
    user = api.get_user(screen_name=accountName)
    # Extract the desired data from the user object
    user_id = user.id

    
    print("--------------------------------------")
    print("\t\t\tAccount Info:")
    print(f"Account ID: {user.id}")
    print(f"Account Name: {user.name}")
    print(f"Account ScreenName: @{user.screen_name}")
    print(f"Account Description: {user.description if (len(user.description) != 0) else None}")    
    print(f"Account Description Entities: {user.entities}")
    print(f"Account Followers Count: {user.followers_count}")
    print(f"Account Friends Count: {user.friends_count}")
    print(f"Account Listed Count: {user.listed_count}")
    print(f"Account Ratio: {user.followers_count / user.friends_count if user.friends_count != 0 else 0:.2f}")
    print(f"Account Created At: {user.created_at}")
    print(f"Account Time Zone: {user.time_zone}")
    print(f"Account Language: {user.lang}")
    print(f"Account Geo Enabled: {user.geo_enabled}")
    print(f"Account Location: {user.location}")
    print(f"Account Profile Image URL: {user.profile_image_url}")
    print(f"Account Protected Tweets: {user.protected}")
    print(f"Account Profile URL: {user.url}")
    print(f"Account Verified: {user.verified}")




    # these are likely broken below:
    #write a if statement to solve the issue below (if pinned_tweet is not None)
    #print(f"Account Pinned Tweet ID: {user.pinned_tweet_id}")
    #fix the part below:
    #print(f"Account Public Metrics: {user.public_metrics}")
    #fix the part below:
    #print(f"Account has withheld content: {user.withheld_scope}")
    #print("")

    print("-----------------------------------------------")
    for tweet in tweepy.Cursor(api.user_timeline, user_id=user_id, tweet_mode='extended').items(5):
        

        print(f"Tweet ID: {tweet.id}")
        print(f"Tweet Created At: {tweet.created_at}")
        print(f"Tweet Text: {tweet.full_text}")
        print(f"Tweet Language: {tweet.lang}")
        print(f"Tweet URL: https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}")
        print(f"Tweet Favorite Count: {tweet.favorite_count}")
        print(f"Tweet Retweet Count: {tweet.retweet_count}")
        print(f"Tweet Mentioned Users: {tweet.entities['user_mentions']}")
        print(f"Tweet Entites: {tweet.entities}")
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
        print(f"Tweet Photo(s) URLs: {tweetPhotoURLs}")
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
        print(f"Tweet Video(s) URLs: {tweetVideoURLs}")
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
        print(f"Tweet URLs: {tweetURLs}")
        print(f"Geo Data: {tweet.geo}")
        #coordinate data
        coordinates = None
        if tweet.place is not None and tweet.place.bounding_box is not None:
            coordinates = tweet.place.bounding_box.centroid
        print(f"Coordinates: {coordinates}")
        print("--------------------------------")



        


"""
scrapTwitterAccount("devapitest4308",
        api_key, 
        api_secret_key,
        access_token, 
        access_token_secret)
"""
scrapTwitterAccount("devapitest4308",
        api_key, 
        api_secret_key,
        access_token, 
        access_token_secret)

#WalmartInc