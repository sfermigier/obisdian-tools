import os

from antidote import Constants, const

CONFIG = {
    "KB_ROOT": "{HOME}/Documents/Notes/",
    "DAILY_NOTES_ROOT": "{HOME}/Documents/Notes/Daily",
    "ICAL_BUDDY_CMD": 'icalBuddy -npc -iep "title,datetime" -b -\  -po "datetime,title" -ps "|: |" eventsToday',
}


class Config(Constants):
    HOME = const[str]()
    KB_ROOT = const[str]()
    DAILY_NOTES_ROOT = const[str]()
    ICAL_BUDDY_CMD = const[str]()

    def provide_const(self, name: str, arg: object):
        if name in os.environ:
            return os.environ[name]

        context = dict(os.environ)
        return CONFIG[name].format(**context)
