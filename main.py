import praw

OUT_STR = """
Title: {}
Text: {}
Score: {}
"""


if __name__ == "__main__":
    reddit = praw.Reddit("bible-bot")
    subreddit = reddit.subreddit("dankchristianmemes")

    for submission in subreddit.hot(limit=5):
        print(OUT_STR.format(submission.title, submission.selftext, submission.score))