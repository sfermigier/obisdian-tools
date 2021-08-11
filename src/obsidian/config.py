import os

from antidote import Constants, const

CONFIG = {
    "KB_ROOT": "{HOME}/Documents/Notes/",
    "DAILY_NOTES_ROOT": "{HOME}/Documents/Notes/Daily",
    "ICAL_BUDDY_CMD": 'icalBuddy -npc -iep "title,datetime" -b -\  -po "datetime,title" -ps "|: |" eventsToday',
    "URL_ROOT": "/notes/",
    "PUBLIC": [
        "Projects/Cython+",
        "Tech/Cloud",
        "Tech/Containers",
        "Tech/Modeling",
        "Tech/Programming techniques",
        "Tech/Python",
        "Tech/Security",
        "Tech/Tools",
        "Tech/Web",
    ],
}


class Config(Constants):
    HOME = const[str]()
    KB_ROOT = const[str]()
    DAILY_NOTES_ROOT = const[str]()
    ICAL_BUDDY_CMD = const[str]()
    PUBLIC = const[list]()
    URL_ROOT = const[str]()

    def provide_const(self, name: str, arg: object):
        if name in os.environ:
            return os.environ[name]

        result = CONFIG[name]
        if not isinstance(result, str):
            return result

        context = dict(os.environ)
        return result.format(**context)
