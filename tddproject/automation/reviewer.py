import requests
import os
import json

def check_update_reviewer(repo, pr, token):

    repository = repo
    pull_num = pr
    base_api = f'https://api.github.com/repos/'
    reviewer_api = f'{repository}/pulls/{pull_num}/requested_reviewers'

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

    try:

        reviewers_check = requests.get(base_api+reviewer_api, headers=headers).json()
        reviewers_requested = reviewers_check['users']
        print(reviewers_requested)

    except Exception as e:

        print(f'Exception occurred with error {e}')    
    
    
    
    

check_update_reviewer(os.getenv('GITHUB_REPOSITORY'),os.getenv('PULL_NUMBER'),os.getenv('GITHUB_TOKEN'))