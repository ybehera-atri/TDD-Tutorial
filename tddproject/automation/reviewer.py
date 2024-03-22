import requests
import os
import json


def check_update_reviewer(repo, pr, token):
    repository = repo
    pull_num = pr
    base_url = f'https://api.github.com/repos/'
    reviewer_api = f'{repository}/pulls/{pull_num}/requested_reviewers'

    headers = {f"Authorization": f"token {token}", f"Accept": f"application/vnd.github+json"}

    # mandatory reviewers
    reviewer_list = ["bruschiusc"]

    # check the current reviewers requested
    try:

        reviewers_check = requests.get(base_url + reviewer_api, headers=headers).json()
        reviewers_requested = reviewers_check['users']
        print(reviewers_requested)

    except Exception as e:

        print(f'Exception occurred with error {e}')

        # if mandatory reviewer not present request
    try:

        list_new = [i for i in reviewer_list if i not in reviewers_requested]

        # payload
        reviewers = {
            f"reviewers": list_new
        }

        reviewer_request = requests.post(base_url + reviewer_api, headers=headers, data=json.dumps(reviewers))

        print(f'{reviewer_request.content} and Status Code is {reviewer_request.status_code}')

    except Exception as e:

        print(f'Exception occurred with erro {e}')

    

# call
check_update_reviewer(os.getenv('GITHUB_REPOSITORY'), os.getenv('PULL_NUMBER'), os.getenv('GITHUB_TOKEN'))
