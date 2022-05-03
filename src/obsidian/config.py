import os

from antidote import Constants, const

from config import CONFIG


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
