# Automation code to create a PR from main to main deployment when version to main is merged
# Automation code to update label as "Deployment" when PR main_3_2 to main_3_2_deployment
# Adds version name to PR
# Associated with trigger_main_to_deployment_pr.yml
# Creates a Release in Github
# Adds commits messages to summary
# Fetches data from Jira to add to GitHub table
# Creates Jira Version
# Updates Jira version with issues
# Creates ticket in Fresh service
# Added checks for Jira, GitHub and Fresh Service
# 

import base64
import time
import requests  # type: ignore
import json
import os
import re
from requests.auth import HTTPBasicAuth  # type: ignore
import pandas as pd  # type: ignore
from tabulate import tabulate  # type: ignore
from datetime import date, timedelta

base_url = f'https://api.github.com/'
base_jira = f'https://atrihub.atlassian.net/'
fresh_service_url = f"https://support.atrihub.io/itil/releases.json"


def pr_create(repo, token, branch, owner, head, pr, jira_token, jira_user, fresh_token):

    repo_name = repo.split('/')[1]  # split repository name
    print(f'The repository is {repo_name}')
    headers = {f"Authorization": f"token {token}",
               f"Accept": f"application/vnd.github+json"}

    payload = {"title": head,
               "head": 'main_yb',  # main_django_3_2
               "base": 'main_yb_deployment',  # main_django_3_2_deployment
               }  # switch branch names in prod
    create_pr_api = f'repos/{repo}/pulls'

    # GitHub APIs
    payload_label = {'labels': ['Deployment']}
    create_label_api = f'repos/{repo}/issues/'
    create_release_api = f'repos/{repo}/releases'
    committer_api = f'repos/{repo}/pulls/{pr}/commits?per_page=100'

    # Freshservice APIs
    freshservice_createticket_api = f'/api/v2/tickets'
    api_key_bytes = f'{fresh_token}:X'.encode('ascii')
    base64_bytes = base64.b64encode(api_key_bytes)
    base64_api_key = base64_bytes.decode('ascii')
    headers_freshser = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {fresh_token}:X"
    }
    ticket_present = False

    # Jira APIs
    version_jira_api = f'rest/api/3/version'
    issue_details_api = f'/rest/api/2/issue/'
    auth = HTTPBasicAuth(jira_user, jira_token)
    headers_jira = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    jira_present = False

    edc_plugins = ['edc_config','edc-plugin-msvr','edc-plugin-image-pipeline','edc-plugin-data-pipeline','edc-meddra','edc_plugin_sae_report','edc_plugin_casebook','edc-bdd']

    # Dataframe
    j_key = []
    desc = []
    j_type = []
    proj_id = []
    proj_n = []
    output_release = []
    summary = '### Summary'
    g_release = '\n\n### Github Releases'
    j_release = '\n\n### JIRA Release'
    j_issue = '\n\n### JIRA Issues'
    release_to = '\n\n### Released to'
    v_name = ''

    # Version name conditions
    try:
        if repo_name == f'TRC_PAD':
            v_name = f'TRC_PAD'
            print(f'Version name in Jira is {v_name}')
            output_release.append("app.aptwebstudy.org")

        elif repo_name == f'TRC_PAD_SRS':
            v_name = f'TRC_PAD_SRS'
            print(f'Version name in Jira is {v_name}')
            output_release.append("srs.aptwebstudy.org")

        elif repo_name == f'EDC':
            v_name = f'EDC {head}'
            print(f'Version name in Jira is {v_name}')
            output_release.append("345.atrihub.org")
            output_release.append("a345-test-1.atrihub.org")
            output_release.append("abcds-test-1.atrihub.org")
            output_release.append("abcds.atrihub.org")
            output_release.append("adni3-test-1.atrihub.org")
            output_release.append("adni3.atrihub.org")
            output_release.append("adni4-test-1.atrihub.org")
            output_release.append("adni4.atrihub.org")
            output_release.append("apex-test-1.atrihub.org")
            output_release.append("apex.atrihub.org")
            output_release.append("bdp-test-1.atrihub.org")
            output_release.append("bdp.atrihub.org")
            output_release.append("beyondd-test-1.atrihub.org")
            output_release.append("beyondd.atrihub.org")
            output_release.append("dart-test-1.atrihub.org")
            output_release.append("dart.atrihub.org")
            output_release.append("leads-test-1.atrihub.org")
            output_release.append("leads.atrihub.org")
            output_release.append("libby-test-1.atrihub.org")
            output_release.append("libby.atrihub.org")
            output_release.append("niad-test-1.atrihub.org")
            output_release.append("niad.atrihub.org")
            output_release.append("nic-test-1.atrihub.org")
            output_release.append("nic.atrihub.org")
            output_release.append("start-test-1.atrihub.org")
            output_release.append("start.atrihub.org")
            output_release.append("trc-test-1.atrihub.org")
            output_release.append("trc.atrihub.org")
            output_release.append("trcds-test-1.atrihub.org")
            output_release.append("trcds.atrihub.org")

        elif repo_name == f'LIMS':
            v_name = f'Version {head}'
            print(f'Version name in Jira is {v_name}')
            output_release.append("lims.atrihub.org")
            output_release.append("lims-test-1.atrihub.org")

        else:
            v_name = f'Version{head}'
            print(f'Version name in Jira is {v_name}')
            output_release.append("345.atrihub.org")
            output_release.append("a345-test-1.atrihub.org")
            output_release.append("abcds-test-1.atrihub.org")
            output_release.append("abcds.atrihub.org")
            output_release.append("adni3-test-1.atrihub.org")
            output_release.append("adni3.atrihub.org")
            output_release.append("adni4-test-1.atrihub.org")
            output_release.append("adni4.atrihub.org")
            output_release.append("apex-test-1.atrihub.org")
            output_release.append("apex.atrihub.org")
            output_release.append("bdp-test-1.atrihub.org")
            output_release.append("bdp.atrihub.org")
            output_release.append("beyondd-test-1.atrihub.org")
            output_release.append("beyondd.atrihub.org")
            output_release.append("dart-test-1.atrihub.org")
            output_release.append("dart.atrihub.org")
            output_release.append("leads-test-1.atrihub.org")
            output_release.append("leads.atrihub.org")
            output_release.append("libby-test-1.atrihub.org")
            output_release.append("libby.atrihub.org")
            output_release.append("niad-test-1.atrihub.org")
            output_release.append("niad.atrihub.org")
            output_release.append("nic-test-1.atrihub.org")
            output_release.append("nic.atrihub.org")
            output_release.append("start-test-1.atrihub.org")
            output_release.append("start.atrihub.org")
            output_release.append("trc-test-1.atrihub.org")
            output_release.append("trc.atrihub.org")
            output_release.append("trcds-test-1.atrihub.org")
            output_release.append("trcds.atrihub.org")

        output_release_str = "\n".join(output_release)

    except Exception as e:
        print(f'Error during Jira Version name conditioning')

    # grab commit messages
    try:
        messageset = set()
        jiratask = set()  # jira issues
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

    except:
        print(f'Commit messages grabbed, no action required')

    # check and create pr if base branch is main, switch main_yb with main_3_2
    try:

        if branch == 'main_yb':
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
                proj = issue_data['fields'].get('project', {})
                proj_name = proj.get('name')  # project name
                if proj_name not in proj_n:
                    proj_n.append(proj_name)
                projid = proj.get('id')  # project id
                j_key.append(tasks)  # lists to input into dataframe
                desc.append(description)
                j_type.append(type_jira)
                if projid not in proj_id:
                    proj_id.append(projid)
                    # print(proj_id)
                # print(f'{tasks}:{description}:{type_jira}')

        print(f'The project in Jira is {proj_n[0]}')

    except Exception as e:
        print(f'Error occurred while fetching issues from Jira {e}')

    # Create Jira release and add release url to github release below
    try:
        if branch == 'main_yb':
            version_name = f'{v_name}38'
            # today = str(date.today())
            print(f'{head} and main_yb merged, creating Jira Release now....')
            print(
                f'Project id is {int(proj_id[0])} and type is {type(int(proj_id[0]))}')
            payload_version = json.dumps({
                "description": "Yashraj Test",
                "name": version_name,
                "projectId": int(proj_id[0]),
            })

            # Add check here for Jira Release

            jira_version_create = requests.post(
                base_jira+version_jira_api, headers=headers_jira, data=payload_version, auth=auth)

            if jira_version_create.status_code == 201:
                print(f'These are the tasks in this PR: {jiratask}')
                new_version = jira_version_create.json()  # id passed to the update jira api
                versionid = new_version['id']
                print(f'Version released in Jira: {versionid}')
                # Add version update here
                issue_payload = {
                    'update': {
                        'fixVersions': [
                            {
                                'add': {'name': version_name}
                            }
                        ]
                    }
                }
                for issue_key in jiratask:
                    issue_version = requests.put(
                        base_jira+issue_details_api+issue_key, headers=headers_jira, data=json.dumps(issue_payload), auth=auth)

                    try:

                        if issue_version.status_code == 204:
                            print(f'{issue_key} added, {issue_version.json()}')
                        else:
                            print(
                                f'Error updating issue {issue_key}, error code {issue_version.status_code} and details: {issue_version.content}')

                    except:
                        print(f'{issue_key}, no action required')

                    time.sleep(2)  # delay before adding the next issue

            else:
                print(
                    f'Error creating Jira Release, {jira_version_create.status_code} and error {jira_version_create.content}')
                jira_present = True

    except Exception as e:
        print(f'Error occurred during Jira Release {e}')

    # Create github release on version main merge
    try:
        if jira_present == False:
            # Jira release url
            release_url = str(base_jira+'projects/' +
                              proj_n[0]+'/versions/'+versionid)
            df = pd.DataFrame({'JIRA-key in Commit': j_key,
                              'JIRA-key': j_key, 'Description': desc, 'Type': j_type, 'Release': version_name})  # dataframe
            df_str = tabulate(df, headers='keys',
                              tablefmt='github', showindex=False)
            print(f'{head} and main_yb merged, creating Github Release')
            set_upd = "\n".join(f"- {line}" for line in messageset)
            payload_release = {f"tag_name": f"{head}",
                               f"name": f"Version {head}",
                               f"body": f"{summary}\n{set_upd}{g_release}\n{j_release}\n{release_url}\n\n{j_issue}\n{df_str}\n{release_to}\n{output_release_str}"}

            # Check here for GitHub Release
            check_git_release = requests.get(
                f'{base_url}{create_release_api}/tags/{head}', headers=headers)

            if check_git_release.status_code == 200:
                print(
                    f'The Release notes, Version {head} is present in Github, skipping Fresh service ticket for further verification')
            else:
                print(
                    f'The Release notes, Version {head} is not present in Github, creating now....')
                release_call = requests.post(
                    base_url+create_release_api, headers=headers, json=payload_release)

                if release_call.status_code == 201:
                    print(f'Release notes created in GitHub')
                    # switch project here with repo name in github # repo
                    github_release = f'https://github.com/atrihub/{repo_name}/releases/tag/{head}'

                    # Check if Fresh service has a ticket with same subject
                    checkticket = requests.get(
                        f'https://support.atrihub.io/itil/releases/filter/new_my_open?format=json', headers=headers_freshser)
                    json_o = json.loads(checkticket.text)
                    # print(f'{json_o}')
                    for release_tick in json_o:
                        if release_tick['subject'] == version_name:
                            #        print(f'{release_tick['display_id']}')
                            ticket_present = True
                            print(f'{version_name} is present')
                            break

                    try:
                        if ticket_present == False:
                            print(
                                f'Ticket is not present in Fresh Service, creating now....')
                            payload_freshser = json.dumps({
                                "itil_release": {
                                    "subject": version_name,
                                    "category": "ATRI SDLC",
                                    # gets project name from Jira
                                    "sub_category": proj_n[0],
                                    "description": f'{github_release}',
                                    "planned_start_date": start_date.strftime(
                                        "%Y-%m-%dT00:00:00-09:00"),
                                    "planned_end_date": end_date.strftime(
                                        "%Y-%m-%dT00:00:00-09:00")
                                }
                            })

                            freshser_response = requests.post(
                                fresh_service_url, headers=headers_freshser, data=payload_freshser)

                            if freshser_response.status_code == 200:
                                print(f'Ticket created successfully')
                                ticket = freshser_response.json()
                                print(f'Ticket ID: {ticket}')
                            else:
                                print(
                                    f'Ticket creation failed, status code: {freshser_response.status_code}, content of error: {freshser_response.text}, url: {fresh_service_url}')

                    except Exception as e:
                        print(
                            f'Error occurred while creating Fresh service ticket, {e}')
                else:
                    print(
                        f'Error creating Release notes {release_call.content}')

        else:
            print(f'Jira version is already present, skipping Github and Fresh Service Release for further examination')

    except Exception as e:
        print(f'Exception occurred during Github release creation {e}')


# call the function with environment variables from yaml as parameters
pr_create(os.getenv('GITHUB_REPOSITORY'), os.getenv('GITHUB_PAT'),
          os.getenv('BRANCH_NAME'), os.getenv('OWNER'), os.getenv('HEAD_BRANCH'), os.getenv(
    'PULL_NUMBER'), os.getenv('JIRA_TOKEN'), os.getenv('JIRA_USERNAME'), os.getenv('FRESHSER_TOKEN'))
