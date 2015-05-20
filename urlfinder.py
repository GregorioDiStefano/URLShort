import random
import sys
import datetime
import time
import logging
from db_model import Shorturls, User

LOG_FILENAME = 'logging.out'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO)


class Tracker(object):

    limit = 30
    reset_time = 0
    ip_tracker = {}

    def set_reset_time(self):
        self.reset_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        self.reset_time = time.mktime(self.reset_time.timetuple())

    def check_access(self, ip):
        current_time = time.mktime(datetime.datetime.utcnow().timetuple())
        if (current_time > self.reset_time):
            logging.info("re-initializing ip tracker")
            self.ip_tracker = {}
            self.set_reset_time()

        if (self.ip_tracker.get(ip, 0) >= self.limit):
            return False
        else:
            self.ip_tracker[ip] = self.ip_tracker.get(ip, 0) + 1
            return True

    def __init__(self):
        self.set_reset_time()


def get_uid():
    """
    Create a list of short url uids.
    The list of uids become progressivly more complex
    Example: ['as', '4s', 's3', 'gd', 'asf', 'fas', 'sda1c0', 'asdg3das']
    """
    uids = []
    characters = "abcdefghjklmnpqrstuv23456789"
    for uid_length in range(2, 12):
        for _ in xrange(25):
            uid = ""
            for counter in xrange(uid_length):
                uid += (characters[random.randint(0, len(characters) - 1)])
            uids.append(uid)
    return uids


def shorturl_already_exists(url):
    try:
        success = Shorturls.get(Shorturls.url == url)
        return success
    except Shorturls.DoesNotExist:
        return False
    except:
        e = sys.exc_info()[0]
        logging.error(e)
        return False


def url_to_uid(url):
    possible_uuids = get_uid()
    success = shorturl_already_exists(url)
    if success:
        return success.uid
    else:
        for uid in possible_uuids:
            try:
                if Shorturls.get(Shorturls.uid == uid):
                    logging.info("%s is already assocaited" % uid)
                    continue
            except Shorturls.DoesNotExist:
                shorturl = Shorturls(user=None,
                                     url=url,
                                     uid=uid,
                                     created=datetime.datetime.now(),
                                     accessed=0)
                shorturl.save()
                print str(shorturl)
                return shorturl.uid



def uid_to_url(uid):
    success = Shorturls.get(Shorturls.uid == uid)
    return success.url


def increase_accessed(uid):
    Shorturls.update(accessed=Shorturls.accessed + 1).where(
    Shorturls.uid == uid).execute()

def save_userinfo(email, hashed_password):
    user = User(email=email,
                password=hashed_password,
                join_date=datetime.datetime.now())
    user.save()

def get_userinfo(email):
    try:
        userinfo = User.get(User.email == email)
    except:
        return False
    else:
        return userinfo


