# Automation code to create a PR from main to main deployment when version to main is merged
# Automation code to update label as "Deployment" when PR main_3_2 to main_3_2_deployment
# Adds version name to PR
# Associated with trigger_main_to_deployment_pr.yml
# Creates a Release in Github
# Adds commits messages to summary
# Fetches data from Jira
#

import requests  # type: ignore
import json
import os
import re
from requests.auth import HTTPBasicAuth  # type: ignore
import pandas as pd  # type: ignore
from tabulate import tabulate # type: ignore
from prettytable import PrettyTable
import textwrap

base_url = f'https://api.github.com/'
base_jira = f'https://atrihub.atlassian.net/'


def pr_create(repo, token, branch, owner, head, pr, jira_token):

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

    # Jira
    version_jira_api = f'rest/api/3/version'
    issue_details_api = f'/rest/api/2/issue/'
    auth = HTTPBasicAuth("ybehera@atrihub.io", jira_token)
    headers_jira = {
        "Accept": "application/json"
    }

    # Dataframe
    j_key = []
    desc = []
    j_type = []
    # release = []

    # grab commit messages
    try:
        messageset = set()
        jiratask = set()
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
                # commit messages in a set
                messageset.add(message.split(']')[0])
            jiratask.add(git_task[0])  # jira tasks from commits in a set
            # print(f"{message.split(']')[0]}:{git_task[0]}")

    except Exception as e:
        print(f'{e}, no action required')

    # check and create pr if base branch is main, switch main_yb with main_3_2
    try:

        if branch == 'main_django_3_2':
            # print(base_url+create_pr_api)
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

    # Get issues data from Jira and update in github release page (JIRA Issues in github release body)
    try:
        for tasks in jiratask:

            jira_issues = requests.get(
                base_jira+issue_details_api+tasks, headers=headers_jira, auth=auth)

            if jira_issues.status_code == 200:
                issue_data = jira_issues.json()

                description = issue_data['fields'].get(
                    'description', 'No description found')
                type_jira = issue_data['fields'].get('issuetype', {}).get(
                    'name', 'No task type found')
                j_key.append(tasks)  # lists to input into dataframe
                desc.append(description)
                j_type.append(type_jira)
                print(f'{tasks}:{description}:{type_jira}')

    except Exception as e:
        print(f'Error occurred while fetching issues from Jira {e}')

    # Create Jira release and add release url to github release below

    # Create github release on version main merge
    try:
        if branch == 'main_django_3_2':
            df = pd.DataFrame({'JIRA-key in Commit': j_key,
                              'JIRA-key': j_key, 'Description': desc, 'Type': j_type})  # dataframe
            df['Description'] = df['Description'].apply(lambda x: '\n'.join(textwrap.wrap(x, width=40)))
            df_str = tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False)
            #df_str = df.to_string(index=False)  # dataframe as string
            print(f'{head} and main_django_3_2 merged, creating Release')
            set_upd = "\n".join(f"- {line}" for line in messageset)
            payload_release = {f"tag_name": f"{head}",
                               f"name": f"Version {head}",
                               f"body": f"## **Summary** \n {set_upd} \n \n \n ## **Github Releases** \n \n \n ## **JIRA Release** \n \n \n ## **JIRA Issues** \n \n {df_str}"}
            release_call = requests.post(
                base_url+create_release_api, headers=headers, json=payload_release)

            if release_call.status_code == 201:
                print(f'Release notes created')
            else:
                print(
                    f'Error creating Release notes {release_call.content}')

    except Exception as e:
        print(f'Exception occurred during release creation {e}')


# call the function with environment variables from yaml as parameters
pr_create(os.getenv('GITHUB_REPOSITORY'), os.getenv('GITHUB_PAT'),
          os.getenv('BRANCH_NAME'), os.getenv('OWNER'), os.getenv('HEAD_BRANCH'), os.getenv(
    'PULL_NUMBER'), os.getenv('JIRA_TOKEN'))
