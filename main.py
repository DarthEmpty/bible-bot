import bible_lookup as bl
import logging
import os.path
import praw
from praw.exceptions import APIException
from ratelimit import limits, sleep_and_retry

SUBREDDIT = "pythonforengineers"
COMMENT_LIMIT = 100
SAVE_FILE = "bookmark.txt"
LOG_FILE = "bible-bot.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"


def load_bookmark():
    with open(SAVE_FILE) as f:
        return f.read()


def save_bookmark(id):
    with open(SAVE_FILE, "w") as f:
        f.write(id)


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
    bookmark = load_bookmark() if os.path.exists(SAVE_FILE) else None

    for comment in comments:
        # Stop if comment has been seen before
        if bookmark == comment.id:
            break

        refs = bl.extract_references(comment.body.replace("\\", ""))
        if refs:
            logging.info("Processing comment " + comment.id)
            
            passages = bl.batch_lookup(refs)
            replies = bl.construct_replies(passages)

            reply_body = "\n---\n".join(replies)
            try:
                reply_to(comment, reply_body)
                logging.info("Successfully reply to " + comment.id)
            except APIException as err:
                logging.error(err.message)

        # Store most recent comment as bookmark
        if comments.yielded == 1:
            save_bookmark(comment.id)
