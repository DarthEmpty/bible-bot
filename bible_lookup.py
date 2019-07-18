import json
from pprint import pprint
import re
import requests


API_STRING = "https://getbible.net/json?text={}&ver={}"
REFERENCE_PATTERN = r"\[\[(.*?)\]\]"


def extract_references(text: str):
    return re.findall(REFERENCE_PATTERN, text)


def lookup(ref: str, version="kjv"):
    response = requests.get(API_STRING.format(ref, version))
    
    if response.status_code != 200:
        return "{}: {}".format(response.status_code, response.reason)

    stripped = response.text.strip("();")
    return json.loads(stripped)


def batch_lookup(refs: list):
    return [ lookup(ref) for ref in refs ]


def construct_reply(passage: dict):
    verses = passage["chapter"]
    verse_numbers = sorted(list(verses.keys()), key=lambda k: int(k))

    reply = "{} {} ({})\n\n".format(passage["book_name"], passage["chapter_nr"], passage["version"])
    for num in verse_numbers:
        reply += "{}: {}".format(num, verses[num]["verse"])

    return reply


def construct_replies(passages: list):
    replies = []

    for passage in passages:
        if "book" in passage:
            for section in passage["book"]:
                section["version"] = passage["version"]

            replies.extend(construct_replies(passage["book"]))
            
        else:
            replies.append(construct_reply(passage))
    
    return replies



if __name__ == "__main__":
    passages = extract_references("I love what Jesus says in [[John3:16-18]] - especially when he says that bit about love in John3:16! Some of my other favourites are [[1 Corinthians 13]] and [[Romans 12:2]]")
    res = batch_lookup(passages)
    replies = construct_replies(res)
    pprint(replies)
