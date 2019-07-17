import json
from pprint import pprint
import re
import requests


API_STRING = "https://getbible.net/json?text={}&ver={}"
REFERENCE_PATTERN = r"\[\[(.*?)\]\]"


def extract_references(text):
    return re.findall(REFERENCE_PATTERN, text)


def lookup(ref, version="kjv"):
    response = requests.get(API_STRING.format(ref, version))
    
    if response.status_code != 200:
        return "{}: {}".format(response.status_code, response.reason)

    stripped = response.text.strip("();")
    return json.loads(stripped)


def batch_lookup(refs):
    return { ref: lookup(ref) for ref in refs }


if __name__ == "__main__":
    passages = extract_references("I love what Jesus says in [[John3:16-18]] - especially when he says that bit about love in John3:16! Some of my other favourites are [[1 Corinthians 13]] and [[Romans 12:2]]")
    pprint(batch_lookup(passages))