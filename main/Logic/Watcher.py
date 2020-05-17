import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SASTest.settings')
django.setup()

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from main.Logic.Check import Check
import datetime


class Watcher:
    def __init__(self):
        # set up the values for the handler
        patterns = "*"
        ignore_patterns = ""
        ignore_directories = False
        case_sensitive = True
        # configure the handler
        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_created = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved
        # set the path for the directory that should be watched
        path = "../Reports"
        go_recursively = True
        # set up the observer to watch the directory
        my_observer = Observer()
        my_observer.schedule(my_event_handler, path, recursive=go_recursively)
        my_observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

    def on_created(self, event):
        '''once a file is created do this stuff'''
        # cut the directory
        xml_file = event.src_path.split('\\')[-1]
        # TODO check if file is on correct format
        # cut the ending
        xml_file = xml_file.split(".")[0]
        # get dates and file name
        dates = xml_file.split("-")
        report_name = dates[-4]
        # set up the correct date
        date = datetime.datetime.strptime("1 May 2020", '%d %b %Y')
        date = date.replace(day=int(dates[-3]), month=int(dates[-2]), year=int(dates[-1]))
        # init the checker
        checker = Check()

        # check different dates based on report category
        if (report_name == "CC050"):
            tomorrow = date + datetime.timedelta(days=1)
            if os.path.exists(
              "../Reports/CI050-{}-{}-{}.xml".format(tomorrow.day, tomorrow.month, tomorrow.year)) and os.path.exists(
                "../Reports/CI050-{}-{}-{}.xml".format(date.day, date.month, date.year)):
                checker.check(tomorrow)
        else:
            yesterday = date - datetime.timedelta(days=1)
            if os.path.exists(
              "../Reports/CC050-{}-{}-{}.xml".format(yesterday.day, yesterday.month, yesterday.year)) and os.path.exists(
                "../Reports/CI050-{}-{}-{}.xml".format(yesterday.day, yesterday.month, yesterday.year)):
                checker.check(date)


    def on_deleted(self, event):
        '''print a message in console if a file is deleted'''
        print(f"Someone deleted {event.src_path}!")


    def on_modified(self, event):
        '''when a file is modified also run the check'''
        self.on_created(event)


    def on_moved(self, event):
        '''log when file is moved'''
        print(f"someone moved {event.src_path} to {event.dest_path}")


if __name__ == "__main__":
    Watcher()
