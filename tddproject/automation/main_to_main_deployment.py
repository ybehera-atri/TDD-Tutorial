# Automation code to create a PR from main to main deployment when version to main is merged
# Automation code to update label as "Deployment" when PR main_3_2 to main_3_2_deployment
# Adds version name to PR
# Associated with trigger_main_to_deployment_pr.yml
# Creates a Release
# Adds commits messages to summary
# 

import requests  # type: ignore
import json
import os
import re

base_url = f'https://api.github.com/'


def pr_create(repo, token, branch, owner, head, pr):

    headers = {f"Authorization": f"token {token}",
               f"Accept": f"application/vnd.github+json"}

    payload = {"title": head,
               "head": 'main_django_3_2',  # main_django_3_2
               "base": 'main_django_3_2_deployment',  # main_django_3_2_deployment
               }  # switch branch names in prod
    create_pr_api = f'repos/{repo}/pulls'

    payload_label = {'labels': ['Deployment']}
    create_label_api = f'repos/{repo}/issues/'
    create_release_api = f'repos/{repo}/releases'
    committer_api = f'repos/{repo}/pulls/{pr}/commits?per_page=100'

    # grab commit messages
    try:
        messageset = set()
        # committers information, user and committ message
        committers_info = requests.get(
            base_url + committer_api, headers=headers)
        committer_text = committers_info.text
        data_json = json.loads(committer_text)
        pattern = r'\b(?:\[)?([a-zA-Z]+-\d+)(?:\])?\b'

        for names in data_json:
            committer_msg = names.get('commit').get("message")
            message = re.sub(pattern, '', committer_msg)
            git_task = re.findall(pattern, committer_msg)
            if 'Merge pull request' not in message:
                messageset.add(message.split(']')[0])
            #print(f"{message.split(']')[0]}:{git_task[0]}")

    except Exception as e:
        print(f'Exception occurred with error {e}')

    # Create release on version main merge
    try:
        if branch == 'main_django_3_2':
            print(f'{head} and main_django_3_2 merged, creating Release')
            set_upd = "\n".join(f"- {line}" for line in messageset)
            payload_release = {f"tag_name": f"{head}",
                               f"name": f"Version {head}",
                               f"body": f"## **Summary**\n {set_upd}"}
            release_call = requests.post(
                base_url+create_release_api, headers=headers, json=payload_release)

            if release_call.status_code == 201:
                print(f'Release notes created')
            else:
                print(
                    f'Error creating Release notes {release_call.content}')

    except Exception as e:
        print(f'Exception occurred during release creation {e}')

    # check and create pr if base branch is main, switch main_yb with main_3_2
    try:

        if branch == 'main_django_3_2':
            print(base_url+create_pr_api)
            create_pr = requests.post(
                base_url+create_pr_api, headers=headers, json=payload)

            if create_pr.status_code == 201:
                print(f'PR from main to main deployment created')
                pull_num = create_pr.json()['number']
                print(f'New Pull number is {pull_num}')

                if pull_num > 0:
                    create_label = requests.post(
                        base_url+create_label_api+str(pull_num)+'/labels', headers=headers, json=payload_label)

                    if create_label.status_code == 200:
                        print(f'Label created')
                    else:
                        print(f'Error creating label, {create_label.content}')

            else:
                print(
                    f'Error creating PR from main to main deployment, error code {create_pr.content}')

    except Exception as e:
        print(f'Error occurred with exception {e}')


# call the function with environment variables from yaml as parameters
pr_create(os.getenv('GITHUB_REPOSITORY'), os.getenv('GITHUB_PAT'),
          os.getenv('BRANCH_NAME'), os.getenv('OWNER'), os.getenv('HEAD_BRANCH'), os.getenv(
    'PULL_NUMBER'))


