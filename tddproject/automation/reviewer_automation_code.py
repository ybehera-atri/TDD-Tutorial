# Automation grabs git tasks and updates to the PR description
# Automation code to request reviewers when a PR is submitted
# Gets triggered automatically on PR to version/main branch
# For feature to version -> adds leadership + committers as reviewers
# For main to main deployment -> adds leadership only
# Adds version name to PR from version to main
# Associated with reviewers_automation_workflow.yml

import requests
import os
import json
import re


def check_update_reviewer(repo, pr, token, branch_name, pruser, head):
    repository = repo
    pull_num = pr
    pr_user = pruser
    branch = branch_name  # base branch name of this PR
    base_url = f'https://api.github.com/'
    reviewer_api = f'repos/{repository}/pulls/{pull_num}/requested_reviewers'
    committer_api = f'repos/{repository}/pulls/{pull_num}/commits?per_page=250'
    update_pr_api = f'repos/{repository}/pulls/{pull_num}'
    create_release_api = f'repos/{repository}/releases'
    user_search = f'search/users?q='

    headers = {f"Authorization": f"token {token}",
               f"Accept": f"application/vnd.github+json"}

    # mandatory reviewers
    reviewer_list = ["bruschiusc"]

    list_new = []
    all_matches = set()
    pattern = r'\b(?:\[)?([a-zA-Z]+-\d+)(?:\])?\b'  # regex to find gittasks

    # committers information, user and committ message
    committers_info = requests.get(base_url + committer_api, headers=headers)
    committer_text = committers_info.text
    data_json = json.loads(committer_text)

    # grab and update git task id to pr body
    try:

        for names in data_json:
            committer_msg = names.get('commit').get("message")

            git_task = re.findall(pattern, committer_msg)
            with_sq = [f'[{t}]' for t in git_task]
            all_matches.update(with_sq)
        formatted_str = '\n'.join(sorted(all_matches))
        print(f'These are the task ids from this PR: {formatted_str}')

        payload = {"body": formatted_str}

        update_pr_body = requests.patch(
            base_url + update_pr_api, headers=headers, json=payload)
        if update_pr_body.status_code == 200:
            print(f'Pull Request is updated with the git task ids')
        else:
            print(
                f'Could not update pull request with git task, error code: {update_pr_body.content}')
    except Exception as e:
        print(f'Exception occurred with error {e}')

    # check the current reviewers requested
    try:

        reviewers_check = requests.get(
            base_url + reviewer_api, headers=headers).json()

        reviewers_requested = reviewers_check['users']  # reviewers
        # list with reviewers not requested
        list_new = [i for i in reviewer_list if i not in reviewers_requested]

        if len(list_new) >= 0:
            print(f'Managers {list_new} missing, adding them as reviewers')

        elif all(x in reviewers_requested for x in reviewer_list):
            print(
                f'All managers {reviewer_list} already requested')

        # Adding committers as reviewers only if base branch is version and extracting messages

        try:
            if branch != 'main_django_3_2_deployment':
                # updates title with version number for version to main pr
                if branch == 'main_django_3_2':
                    try:
                        print(f'Updating title of main')
                        payload = {"title": head}
                        update_pr = requests.patch(
                            base_url+update_pr_api, headers=headers, json=payload)

                        if update_pr.status_code == 200:
                            print(f'Title updated with version')
                        else:
                            print(
                                f'Error updating PR title {update_pr.content}')

                    except Exception as e:
                        print(f'Exception occurred while updating title {e}')

                    try:
                        print(f'Base branch is Main, lets creates release notes')
                        payload_release = {"tag_name": "Test"}
                        release_call = requests.post(
                            base_url+create_release_api, headers=headers, json=payload_release)
                        
                        if release_call.status_code == 201:
                            print(f'Release notes created')
                        else:
                            print(
                                f'Error creating Release notes {release_call.content}')

                    except Exception as e:
                        print(f'Exception occurred while creating release {e}')

                print(f'Base branch is {branch}, fetching committers')
                for names in data_json:
                    committer_email = names.get(
                        'commit').get('author').get('email')
                    committer_uname = committer_email.split(
                        '@')[0]  # split username off the email
                    committer_data = requests.get(
                        f'{base_url}{user_search}{committer_uname}').json()['items'][0]['login']
                    # print(f'{committer_data}')
                    if committer_data not in list_new:
                        list_new.append(committer_data)

                print(f'reviewer list with committers: {list_new}')

            else:
                print(f'Base branch is main deployment, no additional reviewers')

        except Exception as e:
            print(
                f'Reviewer list with committers: {list_new}')

    except Exception as e:

        print(f'Exception occurred with error {e}')

    # removing pr owner as they cannot be added as reviewer
    try:
        for reviewer in list_new:
            if pr_user == reviewer:
                print(f'{reviewer} submitted the PR, removing from reviewer list')
                list_new.remove(reviewer)
                break
    except Exception as e:
        print(f'Exception occured while removing pr user {e}')

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
    'PULL_NUMBER'), os.getenv('GITHUB_TOKEN'), os.getenv('BRANCH_NAME'), os.getenv('PR_USER'), os.getenv('HEAD_BRANCH'))
