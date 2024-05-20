# Automation code to create a PR from main to main deployment when version to main is merged
# Automation code to update label as "Deployment" when PR main_3_2 to main_3_2_deployment
# Adds version name to PR
# Associated with trigger_main_to_deployment_pr.yml

import requests
import json
import os

base_url = f'https://api.github.com/'


def pr_create(repo, token, branch, owner, head):

    headers = {f"Authorization": f"token {token}",
               f"Accept": f"application/vnd.github+json"}

    payload = {"title": head,
               "head": 'main_3_2',  # main_3_2
               "base": 'main_3_2_deployment',  # main_3_2_deployment
               }  # switch branch names in prod
    create_pr_api = f'repos/{repo}/pulls'

    payload_label = {'labels': ['Deployment']}
    create_label_api = f'repos/{repo}/issues/'

    # check and create pr if base branch is main, switch main_yb with main_3_2
    try:

        if branch == 'main_yb' or branch == 'main_3_2':
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
          os.getenv('BRANCH_NAME'), os.getenv('OWNER'), os.getenv('HEAD_BRANCH'))
