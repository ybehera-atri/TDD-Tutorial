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
    branch = os.getenv('BRANCH_NAME')  # base branch name of this PR
    owner = os.getenv('REPO_OWNER')  # repo owner
    committer_api = f'{owner}/{repository}/pulls/{pull_num}/commits'

    # check the current reviewers requested
    try:

        reviewers_check = requests.get(
            base_url + reviewer_api, headers=headers).json()

        reviewers_requested = reviewers_check['users']  # reviewers
        # list with reviewers not requested
        list_new = [i for i in reviewer_list if i not in reviewers_requested]

        if len(list_new) >= 0:
            print(f'Managers {list_new} missing, adding reviewers')

        elif all(x in reviewers_requested for x in reviewer_list):
            print(f'All managers {reviewer_list} already requested, exiting')

    except Exception as e:

        print(f'Exception occurred with error {e}')

    # Adding committers as reviewers if base branch is version
    try:
        if branch != 'main_django_3_2' or 'main_django_3_2_deployment':
            committers_info = requests.get(
                base_url + committer_api, headers=headers)
            print(base_url+committer_api)

            if committers_info.status_code == 200:
                print(
                    f'Base branch is version, committer details {json(committers_info)}')
            else:
                print(f'{committers_info.status_code} and {committers_info.text}')

        else:
            print(f'Base branch is not version, no additional reviewers')
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
