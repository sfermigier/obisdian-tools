import os

from antidote import Constants, const


class Config(Constants):
    HOME = const[str]()
    DAILY_NOTES_ROOT = const[str]()
    ICAL_BUDDY_CMD = const[str]()

    def provide_const(self, name: str, arg: object):
        HOME = os.environ["HOME"]
        if name == "HOME":
            return HOME
        if name == "DAILY_NOTES_ROOT":
            return f"{HOME}/Documents/Notes/Daily"
        if name == "ICAL_BUDDY_CMD":
            return 'icalBuddy -npc -iep "title,datetime" -b -\  -po "datetime,title" -ps "|: |" eventsToday'
