import random
import datetime
import time
import logging

from settings import settings
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


def shorturl_already_exists(url, user):
    try:
        if user:
            success = Shorturls.get(Shorturls.url == url,
                                    Shorturls.user == get_userinfo(user))
        else:
            success = Shorturls.get(Shorturls.url == url,
                                    Shorturls.user == None)
        return success
    except Shorturls.DoesNotExist:
        return False
    except Exception, e:
        logging.error(e)
        return False


def url_to_uid(url, user=None):
    possible_uuids = get_uid()
    success = shorturl_already_exists(url, user)
    if success:
        return success.uid
    for uid in possible_uuids:
        try:
            if Shorturls.get(Shorturls.uid == uid):
                logging.info("%s is already assocaited" % uid)
                continue
        except Shorturls.DoesNotExist:
            user = get_userinfo(user) or None
            shorturl = Shorturls(user=user,
                                 url=url,
                                 uid=uid,
                                 created=datetime.datetime.now(),
                                 accessed=0)
            shorturl.save()
            logging.info(str(shorturl))
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
    except Exception:
        return False
    else:
        return userinfo

def update_password(email, new_password):
    try:
        userinfo = User.get(User.email == email)
        userinfo.password = new_password
        userinfo.save()
    except Exception:
        return False
    else:
        return userinfo

def get_user_urls(email):
    url_list = {}
    url_list["urls"] = []
    try:
        urls = Shorturls.select().where(Shorturls.user == get_userinfo(email))
    except Exception, e:
        logging.error(e)
        return False

    for url in urls:
        url_list["urls"] += [{"url" : settings["domain"] + url.uid,
                              "original_url" : url.url,
                              "created" : str(url.created),
                              "accessed" : url.accessed}]
    return url_list
