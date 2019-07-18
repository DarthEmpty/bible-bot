import bible_lookup as bl
import os.path
import praw

SUBREDDIT = "pythonforengineers"
COMMENT_LIMIT = 500
SAVE_FILE = "bookmark.txt"


def load_bookmark():
    with open(SAVE_FILE) as f:
        return f.read()


def save_bookmark(id):
    with open(SAVE_FILE, "w") as f:
        f.write(id)


if __name__ == "__main__":
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
            passages = bl.batch_lookup(refs)
            replies = bl.construct_replies(passages)
            reply_body = "\n---\n".join(replies)
            comment.reply(reply_body)

        # Store most recent comment as bookmark
        if comments.yielded == 1:
            save_bookmark(comment.id)