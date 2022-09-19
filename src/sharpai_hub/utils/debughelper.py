
import requests
from .get_id import get_id

GA_TRACKING_ID = 'UA-238868007-1'
def event(event_to_send):
    try:
        data = {
            'v': '1',  # API Version.
            'tid': GA_TRACKING_ID,  # Tracking ID / Property ID.
            # Anonymous Client Identifier. Ideally, this should be a UUID that
            # is associated with particular user, device, or browser instance.
            'cid': get_id(),
            't': 'event',  # Event hit type.
            'ec': 'Log',  # Event category.
            'ea': event_to_send,  # Event action.
            'ua': 'Python3'
        }
        response = requests.post('https://www.google-analytics.com/collect', data=data)
    except Exception as e:
        pass
if __name__ == '__main__':
    event('test')