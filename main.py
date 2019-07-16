import os.path
import praw

COMMENT_LIMIT = 100
SAVE_FILE = "bookmark.txt"


def load_bookmark():
    with open(SAVE_FILE) as f:
        return f.read()


def save_bookmark(id):
    with open(SAVE_FILE, "w") as f:
        f.write(id)


if __name__ == "__main__":
    reddit = praw.Reddit("bible-bot")
    subreddit = reddit.subreddit("dankchristianmemes")

    comments = subreddit.comments(limit=COMMENT_LIMIT)
    bookmark = load_bookmark() if os.path.exists(SAVE_FILE) else None

    for comment in comments:
        # Stop if comment has been seen before
        if bookmark == comment.id:
            break

        # Store most recent comment as bookmark
        if comments.yielded == 1:
            save_bookmark(comment.id)

    
    