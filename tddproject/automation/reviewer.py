# Automation code to request reviewers when a PR is submitted
# Gets triggered automatically on PR to feature branch

import requests
import os
import json


def check_update_reviewer(repo, pr, token):
    repository = repo
    pull_num = pr
    base_url = f'https://api.github.com/repos/'
    reviewer_api = f'{repository}/pulls/{pull_num}/requested_reviewers'

    headers = {f"Authorization": f"token {token}",
               f"Accept": f"application/vnd.github+json"}

    # mandatory reviewers
    reviewer_list = ["bruschiusc"]

    # check the current reviewers requested
    try:

        reviewers_check = requests.get(
            base_url + reviewer_api, headers=headers).json()

        reviewers_requested = reviewers_check['users']  # reviewers
        # list with reviewers not requested
        list_new = [i for i in reviewer_list if i not in reviewers_requested]

        if len(reviewer_list) == 0:
            print(f'No reviewers requested, adding reviewers')
        elif all(x in reviewers_requested for x in reviewer_list):
            print(f'All reviewers {reviewer_list} already requested, exiting')
        elif len(list_new) > 0:
            print(f'Adding the reviewers {list_new}')

    except Exception as e:

        print(f'Exception occurred with error {e}')

        # if mandatory reviewer not present request
    try:

        # payload
        reviewers = {
            f"reviewers": list_new
        }

        reviewer_request = requests.post(
            base_url + reviewer_api, headers=headers, data=json.dumps(reviewers))

        if reviewer_request.status_code == 201:

            print(f'Reviewers {list_new} added to the PR')

    except Exception as e:

        print(f'Exception occurred with erro {e}')


# call the function with environment variables from yaml as parameters
check_update_reviewer(os.getenv('GITHUB_REPOSITORY'), os.getenv(
    'PULL_NUMBER'), os.getenv('GITHUB_TOKEN'))
