import glob
import os
import re
import subprocess
import sys

import arrow
import requests
from antidote import world
from devtools import debug

from obsidian.config import Config


def get_link_for_file(file, link_text=""):
    if link_text != "":
        return "[[" + file.replace(".md", "") + "|" + link_text + "]]"
    else:
        return "[[" + file.replace(".md", "") + "]]"


def get_weather():
    payload = {"format": "4"}
    r = requests.get("https://wttr.in/", params=payload)
    return r.text.strip()


def read_file(file_name):
    file_content = ""
    with open(file_name, "r") as file_obj:
        for line in file_obj:
            file_content += line
    return file_content


def get_humanize_date_from_daily_note(file_name):
    daily_note = re.search(
        "\d{4}\.\d{2}\.\d{2}\.[A-Za-z]{3}",
        os.path.basename(file_name).replace(".md", ""),
    )
    if daily_note:
        (year, mon, day, _) = os.path.basename(file_name).replace(".md", "").split(".")
        todo_date = arrow.get(year + "-" + mon + "-" + day)
        return " (from " + todo_date.humanize() + ")"
    else:
        return ""


def get_daily_notes_filename(offset=0):
    file_date = arrow.now()
    if offset != 0:
        file_date = file_date.shift(days=offset)
    return file_date.format("YYYY-MM-DD") + ".md"


def find_todos_in_file(file_name, pattern):
    # Search a file for incomplete todos: [ ]
    # Strip the item down to its bare essentials
    # Hash it to eliminate duplicates
    matches = {}
    with open(file_name, "r") as file_obj:
        for line in file_obj:
            todo = ""
            result = re.search(pattern, line.strip())
            if result:
                if result.group(1):
                    todo = result.group(1).strip()
                    if " (from " in todo:
                        pos = todo.find("(from ")
                        todo = todo[:pos].strip()
                    else:
                        todo = todo.strip()
                    matches[todo] = file_name
    return matches


def search_in_file(file_name, search_for):
    # Searches file_name for search_for and returns boolean result
    with open(file_name, "r") as fd:
        for line in fd:
            if search_for in line:
                return True
    return False


def get_done_todos():
    done_task_pattern = "\[x\](.*)"
    return get_todos(done_task_pattern)


def get_open_todos():
    open_task_pattern = "\[\s\](.*)"
    return get_todos(open_task_pattern)


def get_todos(pattern):
    todos = {}

    daily_notes = world.get[str](Config.DAILY_NOTES_ROOT)

    for filename in glob.glob(daily_notes + "/*.md"):
        fi_done = find_todos_in_file(filename, pattern)
        if fi_done and "x" not in pattern:
            print("Error please investigate")
            debug(filename, fi_done)
            # raise Exception("Error please investigate")
        for m in fi_done:
            if m in todos.keys():
                continue
            todos[m] = fi_done[m]
    return todos


def get_agenda():
    # for this to work with icalBuddy (as of 1/31/21) a special version of the
    # binary is needed (see this thread https://forum.keyboardmaestro.com/t/icalbuddy-doesnt-work-within-keyboard-maestro-mojave-calendar-permissions/15446/5)
    # I replaced the exsting version in /opt/homebrew/cellar/bin moving the old
    # version to icalBuddy.old. The fixed version is in my Downloads folder
    # Also, you need to run it from Finder the first time using right-click Open so
    # that you can okay the binary to run on the local machine.
    ical_buddy = world.get[str](Config.ICAL_BUDDY_CMD)
    result = subprocess.getoutput(ical_buddy)
    return result


def generate_file(fh):
    tasks = {}
    agenda = get_agenda().split("\n")

    # Make note navigation
    nav_bar = get_link_for_file(get_daily_notes_filename(offset=-1))
    nav_bar += " | " + get_link_for_file(get_daily_notes_filename(offset=1))
    nav_bar += " | " + get_weather()
    fh.write(nav_bar + "\n")

    fh.write("\n## Agenda\n")
    if len(agenda) == 1:
        fh.write("Nothing in today's calendar\n")
    else:
        for item in agenda:
            fh.write(item + "\n")

    done_todos = get_done_todos()
    open_todos = get_open_todos()

    for task in open_todos.keys():
        if task in done_todos.keys():
            continue
        else:
            tasks[task] = open_todos[task]

    fh.write("\n## To-Do\n")
    if len(tasks) == 0:
        fh.write("No open to-do items\n")
    else:
        for item in tasks:
            fh.write(
                "- [ ] " + item + get_humanize_date_from_daily_note(tasks[item]) + "\n"
            )

    fh.write("\n## Reading\n")

    fh.write("\n## Today's notes\n")


def daily():
    # Put it all together
    daily_notes = world.get[str](Config.DAILY_NOTES_ROOT)
    daily_notes_file = os.path.join(daily_notes, get_daily_notes_filename())

    if os.path.exists(daily_notes_file):
        print("File already exists. Not overwriting...")
        sys.exit()

    else:
        print(
            "Generating daily notes file " + os.path.basename(daily_notes_file) + "..."
        )
        with open(daily_notes_file, "w") as fh:
            generate_file(fh)
