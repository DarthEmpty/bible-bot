import json
import logging
from pprint import pprint
from ratelimit import limits, sleep_and_retry
import re
import requests


API_STRING = "https://getbible.net/json?text={}"

# Matches with:
# <book><chapter> (book may have digit as prefix)
# <book><chapter>:<verse>
# <book><chapter>:<verse>-<verse>
REFERENCE_PATTERN = "\[\[(\d?[a-zA-Z]+\d+(?::\d+(?:-\d+)?)?)\]\]"


def extract_references(text: str):
    return re.findall(REFERENCE_PATTERN, text.replace(" ", ""))


@sleep_and_retry
@limits(calls=2, period=1)
def lookup(ref: str):
    logging.info("Looking up {}...".format(ref))
    
    response = requests.get(API_STRING.format(ref))
    
    if response.status_code != 200 or response.text == "NULL":
        logging.error("{}: {}".format(response.status_code, response.reason))
        return ""

    stripped = response.text.strip("();")
    return json.loads(stripped)


def batch_lookup(refs: list):
    return [ lookup(ref) for ref in refs ]    


def construct_reply(passage: dict):
    chapter = passage["chapter"]
    verse_numbers = sorted(list(chapter.keys()), key=lambda k: int(k))

    reply = "{} {} ({})\n\n".format(passage["book_name"], passage["chapter_nr"], passage["version"])
    for num in verse_numbers:
        reply += "^({}) {}".format(num, chapter[num]["verse"])

    return reply


def construct_replies(passages: list):
    replies = []

    for passage in passages:
        if passage["type"] == "chapter":
            replies.append(construct_reply(passage))
            
        elif passage["type"] == "verse":
            for chapter in passage["book"]:
                chapter["version"] = passage["version"]
                replies.append(construct_reply(chapter))

        else:
            replies.append("Could not find requested passage")
    
    return replies


if __name__ == "__main__":
    refs = extract_references("""
        I love what Jesus says in [[John 3: 16 - 18]] - especially when he says that bit about love in John3:16!
        Some of my other favourites are [[1 Corinthians 13]] and [[Romans 12:2]]
    """)
    passages = batch_lookup(refs)
    replies = construct_replies(passages)
    print(replies)
