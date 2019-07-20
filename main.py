import bible_lookup as bl
import logging
import os.path
import praw
from praw.exceptions import APIException
from ratelimit import limits, sleep_and_retry

SUBREDDIT = "pythonforengineers"
COMMENT_LIMIT = 100
SAVE_FILE = "read_comments.txt"
LOG_FILE = "bible-bot.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"


def load_read_comments():
    with open(SAVE_FILE) as f:
        return f.readlines()


def save_read_comments(ids):
    with open(SAVE_FILE, "w") as f:
        f.writelines(ids)


@sleep_and_retry
@limits(calls=2, period=1)
def reply_to(comment, body):
    comment.reply(body)


if __name__ == "__main__":
    logging.basicConfig(
        filename=LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )

    reddit = praw.Reddit("bible-bot")
    subreddit = reddit.subreddit(SUBREDDIT)

    comments = subreddit.comments(limit=COMMENT_LIMIT)
    read_comments = load_read_comments() if os.path.exists(SAVE_FILE) else None
    new_read_comments = []

    for comment in comments:
        # Skip comments that have been read before
        if read_comments and comment.id in read_comments:
            continue

        refs = bl.extract_references(comment.body.replace("\\", ""))
        if refs:
            logging.info("Processing comment " + comment.id)

            passages = bl.batch_lookup(refs)
            replies = bl.construct_replies(passages)

            reply_body = "\n---\n".join(replies)
            try:
                reply_to(comment, reply_body)
                new_read_comments.append(comment.id)
                logging.info("Successfully reply to " + comment.id)
            except APIException as err:
                logging.error("{}: {}".format(err.error_type, err.message))


    save_read_comments(new_read_comments)
