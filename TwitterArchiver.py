import requests
import json

def create_headers(bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers

def get_user_id(headers, username):
    base_url = "https://api.twitter.com/2"
    url = f"{base_url}/users/by/username/{username}"

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Request returned an error: {response.status_code}, {response.text}")

    user_data = response.json()
    return user_data['data']['id']

def get_tweets(headers, user_id, username):
    tweets_data = []
    base_url = "https://api.twitter.com/2"
    max_results = 100
    pagination_token = None

    while True:
        if pagination_token:
            url = f"{base_url}/users/{user_id}/tweets?expansions=attachments.media_keys&media.fields=url,type&tweet.fields=attachments,entities,geo,public_metrics&max_results={max_results}&pagination_token={pagination_token}"
        else:
            url = f"{base_url}/users/{user_id}/tweets?expansions=attachments.media_keys&media.fields=url,type&tweet.fields=attachments,entities,geo,public_metrics&max_results={max_results}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Request returned an error: {response.status_code}, {response.text}")

        tweet_data = response.json()
        
        media_dict = {}
        if 'includes' in tweet_data and 'media' in tweet_data['includes']:
            for media in tweet_data['includes']['media']:
                media_dict[media['media_key']] = {'url': media.get('url'), 'type': media['type']}  # Use .get() method for 'url'

        for tweet in tweet_data['data']:
            tweet_text = tweet['text']
            favorite_count = tweet['public_metrics']['like_count']
            retweet_count = tweet['public_metrics']['retweet_count']
            tweet_url = f"https://twitter.com/{username}/status/{tweet['id']}"
            
            entities = tweet.get('entities', {})
            hashtags = [hashtag['tag'] for hashtag in entities.get('hashtags', [])]
            mentioned_users = [user['username'] for user in entities.get('mentions', [])]
            
            in_reply_to_screen_name = None  # The Twitter API v2 does not provide this field directly
            geo_data = tweet['geo'] if 'geo' in tweet else None
            media_URLs = []
            media_type = None

            if 'attachments' in tweet and 'media_keys' in tweet['attachments']:
                media_keys = tweet['attachments']['media_keys']
                media_URLs = [media_dict[key]['url'] for key in media_keys if media_dict[key]['url'] is not None]  # Check if the url is not None

                media_types = list(set([media_dict[key]['type'] for key in media_keys]))
                if len(media_types) == 1:
                    if media_types[0] == 'photo':
                        media_type = 'image' if len(media_keys) == 1 else 'images'
                    else:
                        media_type = media_types[0]

            tweets_data.append([
                tweet_text,
                favorite_count,
                retweet_count,
                tweet_url,
                hashtags,
                mentioned_users,
                in_reply_to_screen_name,
                geo_data,
                media_URLs,
                media_type
            ])

        if 'meta' in tweet_data and 'next_token' in tweet_data['meta']:
            pagination_token = tweet_data['meta']['next_token']
        else:
            break

    return tweets_data

def main():
    # Replace this value with your own Bearer Token
    bearer_token = ""

    headers = create_headers(bearer_token)

    # Replace 'twitter_account' with the account you want to fetch tweets from
    username = "RaspberryPi_org"
    user_id = get_user_id(headers, username)
    tweets_data = get_tweets(headers, user_id, username)

    print(json.dumps(tweets_data, indent=2))

if __name__ == "__main__":
    main()
