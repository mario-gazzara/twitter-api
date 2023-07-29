from services.twitter_api_service import TwitterAPIService
from twitter_client import TwitterClient, TwitterClientOptions

if __name__ == '__main__':
    user_id = 'gazzmarion@gmail.com'
    alternate_user_id = 'gazzaramario'
    password = 'Nutellone99!'

    with TwitterClient(TwitterClientOptions(
        min_wait_time=1,
        max_wait_time=2,
    )) as twitter_client:
        twitter_api_service = TwitterAPIService(twitter_client)

        twitter_api_service.authenticate(user_id, alternate_user_id, password)
