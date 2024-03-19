import requests
import os
import json

def check_reviewer(repo, pr):

    print(repo)
    print(pr)

check_reviewer(os.getenv('GITHUB_REPOSITORY'),os.getenv('PULL_NUMBER'))