import bible_lookup as bl
from collections import deque
import json
import logging
import os.path
import praw
from praw.exceptions import APIException
from ratelimit import limits, sleep_and_retry

SUBREDDIT = "pythonforengineers"
COMMENT_LIMIT = 200
SAVE_FILE = "read_comments.json"
LOG_FILE = "bible-bot.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"


def load_read_comments():
    with open(SAVE_FILE) as f:
        return json.loads(f.read())


def save_read_comments(ids):
    with open(SAVE_FILE, "w") as f:
        f.write(json.dumps(ids))


@sleep_and_retry
@limits(calls=2, period=1)
def reply_to(comment, body):
    comment.reply(body)


def process_comments_in(subreddit, read_comments):
    new_comment_to_save = False
    comments = subreddit.comments(limit=COMMENT_LIMIT)

    for comment in comments:
        # Skip comments that have been read before
        if comment.id in read_comments:
            continue

        refs = bl.extract_references(comment.body)
        if refs:
            logging.info("Processing comment " + comment.id)

            passages = bl.batch_lookup(refs)
            replies = bl.construct_replies(passages)

            reply_body = "\n---\n".join(replies)
            try:
                reply_to(comment, reply_body)
                read_comments.append(comment.id)
                new_comment_to_save = True
                logging.info("Successfully reply to " + comment.id)
            except APIException as err:
                logging.error("{}: {}".format(err.error_type, err.message))

    if new_comment_to_save:
        save_read_comments(list(read_comments))


if __name__ == "__main__":
    logging.basicConfig(
        filename=LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )

    reddit = praw.Reddit("bible-bot")
    subreddit = reddit.subreddit(SUBREDDIT)

    read_comments = deque(
        load_read_comments() if os.path.exists(SAVE_FILE) else [],
        COMMENT_LIMIT
    )

    while True:
        process_comments_in(subreddit, read_comments)
