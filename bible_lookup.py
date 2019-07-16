import json
from pprint import pprint
import requests


API_STRING = "https://getbible.net/json?text={}&ver={}"


def lookup(ref, version="kjv"):
    response = requests.get(API_STRING.format(ref, version))
    
    if response.status_code != 200:
        return str(response.status_code)

    stripped = response.text.strip("();")
    return json.loads(stripped)


if __name__ == "__main__":
    pprint(lookup("John3:16-18"))