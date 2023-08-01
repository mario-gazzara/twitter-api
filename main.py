import os
import pprint

from services.modules.auth.twitter_auth_api_module import TwitterAuthAPIModule
from services.modules.timeline.twitter_home_timeline_api_module import TwitterHomeTimelineAPIModule
from services.twitter_api_service import TwitterAPIService
from twitter_client import TwitterClient, TwitterClientOptions

if __name__ == '__main__':
    user_id = os.environ['TWITTER_USER_ID']
    alternate_user_id = os.environ['TWITTER_ALTERNATE_USER_ID']
    password = os.environ['TWITTER_PASSWORD']

    with TwitterClient(TwitterClientOptions(
        min_wait_time=1,
        max_wait_time=2,
    )) as twitter_client:
        twitter_auth_api_module = TwitterAuthAPIModule(twitter_client)
        twitter_home_timeline_api_module = TwitterHomeTimelineAPIModule(twitter_client)
        twitter_api_service = TwitterAPIService(twitter_auth_api_module, twitter_home_timeline_api_module)

        login_succeded = twitter_api_service.login(user_id, alternate_user_id, password)

        if not login_succeded:
            print('Authentication failed')
            exit(1)

        print('Authentication succeeded')

        # Get Home Timeline

        timeline = twitter_api_service.get_home_timeline()

        if timeline is None:
            print('Failed to get home timeline')
            exit(1)

        print('Home timeline retrieved')

        pp = pprint.PrettyPrinter(indent=4)

        for tweet in timeline.tweets:
            print('Tweet: ' + tweet.id)
            print('Text: ' + tweet.content)
            print('Author: ' + tweet.author.full_name)
            print('\n#############################################\n')
