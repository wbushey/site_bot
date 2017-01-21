# -*- coding: utf8 -*-
import os
from Git.Client import GitClient
from Meetup.Client import MeetupClient
from Meetup.Event import MeetupEvent
from Meetup.Filters import filter_events
from Meetup.Writer import MeetupWriter

REPO_RELATIVE_PATH = 'opentwincities.github.com/'
REPO_AUTHOR_NAME = os.environ['SITE_BOT_REPO_AUTHOR_NAME']
REPO_AUTHOR_EMAIL = os.environ['SITE_BOT_REPO_AUTHOR_EMAIL']
MEETUP_GROUP_NAME = os.environ['SITE_BOT_MEETUP_GROUP_NAME']
MEETUP_API_KEY = os.environ['SITE_BOT_MEETUP_API_KEY']
EVENT_POSTS_DIR = os.path.join(REPO_RELATIVE_PATH, 'events', '_posts')

meetup = MeetupClient(MEETUP_API_KEY, MEETUP_GROUP_NAME)
git = GitClient(REPO_RELATIVE_PATH, REPO_AUTHOR_NAME, REPO_AUTHOR_EMAIL)


def time_to_search_from():
    # TODO Make this read from a file instead of generating a time
    # Returning 1 month ago
    import time
    return int(round((time.time() - 2592000) * 1000))


def poll_and_update():
    events = filter_events(meetup.events, time_to_search_from())

    if events:
        git.reset_hard()
        git.pull()

        writer = MeetupWriter(EVENT_POSTS_DIR)
        for event in events:
            # TODO: Note the first observation of an event in a database, use
            # that for filenames
            writer.write(MeetupEvent(event))

        if git.status:
            git.stage_all()
            git.commit()
            try:
                git.push()
                # TODO write time to file if successful
            except:
                git.remove_head_commit()
