# Automation code to fetch jira issues from commit messages and update it to the PR description
# Workflow triggered when PR is submitted

import os
import requests
import json


def fetch_update_pr(repo, pr, token):
    repository = repo
    pull_num = pr
    base_url = f"https://api.github.com/repos/"
    commits_pr_api = f"{repository}/pulls/{pull_num}/commits"

    headers = {f"Authorization": f"token {token}", f"Accept": f"application/vnd.github+json"}

    response = requests.get(base_url + commits_pr_api, headers=headers).json()

    #print(f"The status code {response.status_code}")

    for commits_message in response['message']:
        print(f"The messages are {commits_message}")


# call the function with environment variables from yaml as parameters
fetch_update_pr(os.getenv('GITHUB_REPOSITORY'), os.getenv('PULL_NUMBER'), os.getenv('GITHUB_TOKEN'))
