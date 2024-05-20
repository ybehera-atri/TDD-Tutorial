import json
import re
import subprocess
from urllib.parse import urljoin
from uuid import uuid4
import requests
from requests.auth import HTTPBasicAuth
from datetime import timedelta, date
# class GitHubConfig():
#     GITHUB_TOKEN_SB_MAC_RUN_CHECK_RELEASE = ""
#     SB_JIRA_TOKEN = ''
#     SB_JRIA_USERNAME = ''
#     SB_FRESH_SERVICE = ""
from deployment.config import GitHubConfig


class GitHubAPI(GitHubConfig):

    def get_release_note(self, jira_version, log_jira_issue, repository,
                         log_file, git_hub_release_tag, description,
                         plugin_repository=[]):
        output_relase = []
        output_relase.append("### Summary")
        output_relase.append(description)
        output_relase.append("\n\n### GitHub Releases")
        if repository.find('edc') >= 0 and repository != 'edc':
            output_relase.append(
                "\n\nhttps://github.com/atrihub/EDC/releases/tag/{0}".format(
                    git_hub_release_tag))
        for r in plugin_repository:
            output_relase.append(
                "\n\nhttps://github.com/atrihub/{1}/releases/tag/{0}".format(
                    git_hub_release_tag, r))
        output_relase.append("\n\n### JIRA Release")
        for key in jira_version.keys():
            output_relase.append(
                "https://atrihub.atlassian.net/projects/{0}/versions/{1}".format(
                    key, jira_version[key]['id']))
        output_relase.append("\n\n### JIRA Issues")
        output_relase.append("\n")
        output_relase.append(
            "|JIRA-key in Commit | JIRA-key | Description | Type | Release |")
        output_relase.append("| --- |--- |--- |--- |--- |")
        for item in log_jira_issue:
            output_relase.append(item)
        output_relase.append("\n\n### Released to")
        if repository == 'TRC_PAD':
            output_relase.append("app.aptwebstudy.org")
        elif repository == 'TRC_PAD_SRS':
            output_relase.append("srs.aptwebstudy.org")
        elif repository == 'LIMS':
            output_relase.append("lims.atrihub.org")
            output_relase.append("lims-test-1.atrihub.org")
        else:
            output_relase.append("345.atrihub.org")
            output_relase.append("a345-test-1.atrihub.org")
            output_relase.append("abcds-test-1.atrihub.org")
            output_relase.append("abcds.atrihub.org")
            output_relase.append("adni3-test-1.atrihub.org")
            output_relase.append("adni3.atrihub.org")
            output_relase.append("adni4-test-1.atrihub.org")
            output_relase.append("adni4.atrihub.org")
            output_relase.append("apex-test-1.atrihub.org")
            output_relase.append("apex.atrihub.org")
            output_relase.append("bdp-test-1.atrihub.org")
            output_relase.append("bdp.atrihub.org")
            output_relase.append("beyondd-test-1.atrihub.org")
            output_relase.append("beyondd.atrihub.org")
            output_relase.append("dart-test-1.atrihub.org")
            output_relase.append("dart.atrihub.org")
            output_relase.append("leads-test-1.atrihub.org")
            output_relase.append("leads.atrihub.org")
            output_relase.append("libby-test-1.atrihub.org")
            output_relase.append("libby.atrihub.org")
            output_relase.append("niad-test-1.atrihub.org")
            output_relase.append("niad.atrihub.org")
            output_relase.append("nic-test-1.atrihub.org")
            output_relase.append("nic.atrihub.org")
            output_relase.append("start-test-1.atrihub.org")
            output_relase.append("start.atrihub.org")
            output_relase.append("trc-test-1.atrihub.org")
            output_relase.append("trc.atrihub.org")
            output_relase.append("trcds-test-1.atrihub.org")
            output_relase.append("trcds.atrihub.org")

        output_relase_str = "\n".join(output_relase)

        with open(log_file, "a") as f:
            f.write('-------------------- \n')
            f.write('SUMMARY \n')
            f.write('-------------------- \n')
            f.write("\n")
            f.write(output_relase_str)
            f.closed

        print(output_relase_str)
        return output_relase_str

    def run(self, repository,
            feature_version,
            feature_master):
        repo_folder = "repo{0}".format(uuid4())
        log_file_row = "/tmp/{1}/{0}/git_log_diff".format(repo_folder,
                                                          repository)
        log_file_jira_list = "/tmp/{1}/{0}/jira_issues_list".format(
            repo_folder,
            repository)

        # get the repository and create list of diff
        params = {
            'token': self.GITHUB_TOKEN_SB_MAC_RUN_CHECK_RELEASE,
            'feature_version': feature_version,
            'feature_master': feature_master,
            'log_file_row': log_file_row,
            'repo_folder': repo_folder,
            'repository': repository}
        list_action = """        
            cd /tmp/
            mkdir /tmp/{repository}
            mkdir /tmp/{repository}/{repo_folder}
            cd /tmp/{repository}/{repo_folder}
            git clone https://bruschiusc:{token}@github.com/atrihub/{repository}.git
            cd /tmp/{repository}/{repo_folder}/{repository}
            ls -a
            git checkout {feature_version}
            git branch
            git checkout -t origin/{feature_master}
            git branch
            git log --no-merges {feature_version} --not {feature_master} > {log_file_row}
        """.format(**params)
        print(list_action)
        subprocess.call(list_action, shell=True)

        # open diff file and extract JIRA issues
        with open(log_file_row, "rb+") as f:
            line = f.read()
        f.closed

        finds = re.findall("\w+-\d+", str(line))
        print(finds)
        finds_unique = sorted(list(set(finds)))
        print(finds_unique)

        with open(log_file_jira_list, "w") as f:
            for item in finds_unique:
                f.write(item)
                f.write("\n")
        f.closed

        return {
            'finds_unique': finds_unique,
            'log_file': log_file_jira_list
        }

    def create_release(self, repository, git_hub_release_tag,
                       target_commitish, body):
        if git_hub_release_tag is None:
            return

        url = "https://api.github.com/repos/atrihub/{0}/releases".format(
            repository)
        response = requests.post(
            url,
            json={
                "tag_name": git_hub_release_tag,
                "target_commitish": target_commitish,
                "name": "Version {}".format(
                    git_hub_release_tag),
                "prerelease": False,
                "draft": True,
                "body": body
            },
            headers={
                "Authorization": "token {0}".format(
                    self.GITHUB_TOKEN_SB_MAC_RUN_CHECK_RELEASE)
            }
        )
        print(response.content)
        content = str(response.content)
        print(json.loads(response.content)['html_url'])


class JiraAPI(GitHubConfig):
    JIRA_URL = "https://atrihub.atlassian.net"

    def __init__(self):
        self.AUTH = HTTPBasicAuth(self.SB_JRIA_USERNAME,
                                  self.SB_JIRA_TOKEN)
        self.HEADERS = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_version(self,
                       project_name_l,
                       project_ids,
                       jira_project_release_name,
                       log_file):
        output = {}

        for project_name in project_name_l:

            if project_name not in project_ids.keys():
                print('project_name {0} not found '.format(project_name))
                continue

            payload = json.dumps({
                "archived": False,
                "name": jira_project_release_name,
                "description": "An excellent version",
                "projectId": project_ids[project_name],
                "released": False
            })

            response = requests.request(
                "POST",
                urljoin(self.JIRA_URL, "rest/api/3/version"),
                data=payload,
                headers=self.HEADERS,
                auth=self.AUTH
            )
            json_o = json.loads(response.text)
            if 'errors' not in json_o.keys():
                output[project_name] = json_o
            else:
                if json_o['errors']['name'] == \
                        'A version with this name already exists in this project.':
                    output[project_name] = self.get_version(
                        project_ids[project_name],
                        jira_project_release_name)
                else:
                    output[project_name] = response.text

        with open(log_file, "a") as f:
            f.write("\n")
            f.write(
                json.dumps(output, sort_keys=True, indent=4,
                           separators=(",", ": ")))
            f.write("\n")
        f.closed

        return output

    def get_version(self, project_id, jira_project_release_name):

        response = requests.request(
            "GET",
            urljoin(self.JIRA_URL,
                    "/rest/api/2/project/{0}/versions".format(project_id)),
            headers=self.HEADERS,
            auth=self.AUTH
        )
        json_o = json.loads(response.text)

        for item in json_o:
            if item['name'] == jira_project_release_name:
                return item
        return None

    def get_project_ids(self):
        response = requests.request(
            "GET",
            urljoin(self.JIRA_URL, "rest/api/3/project"),
            headers=self.HEADERS,
            auth=self.AUTH
        )
        json_o = json.loads(response.text)

        project_ids = {x['key']: x['id'] for x in json_o}
        return project_ids

    def link_jira_to_version(self, jira_issue, jira_project_release_name):

        payload = json.dumps({
            "update": {"fixVersions": [
                {"add": {"name": jira_project_release_name}}
            ]}})
        response = requests.request(
            "PUT",
            urljoin(self.JIRA_URL,
                    "/rest/api/2/issue/{0}".format(jira_issue)),
            data=payload,
            headers=self.HEADERS,
            auth=self.AUTH
        )
        print([jira_issue, 'link jira_issue', response.text])

    def append_summary_log(self, finds_unique, log_file):
        log_jira_issue = list()

        with open(log_file, "a") as f:
            f.write('SUMMARY')
            f.write("\n")
            f.write(
                "|JIRA-key in Commit | JIRA-key | Description | Type | Release |")
            f.write("| --- |--- |--- |--- |--- |")

            for jira_issue in finds_unique:
                response = requests.request(
                    "GET",
                    urljoin(self.JIRA_URL,
                            "/rest/api/2/issue/{0}".format(
                                jira_issue)),
                    headers=self.HEADERS,
                    auth=self.AUTH
                )
                json_o = json.loads(response.text)

                jira_key = 'not found'
                jira_summary = ""
                jira_name = ""
                version = ''
                try:
                    jira_key = json_o['key']
                    jira_summary = json_o['fields']['summary']
                    jira_name = json_o['fields']['issuetype']['name']
                    version = json_o['fields']['fixVersions'][0]['name']
                except:
                    pass

                info_list = (jira_issue,
                             jira_key,
                             jira_summary,
                             jira_name,
                             version,
                             )
                tmp_str = str(' | ').join(info_list)
                tmp_str = "| {0} |".format(tmp_str)
                f.write(tmp_str)
                log_jira_issue.append(tmp_str)
            f.closed
        return log_jira_issue

    def transition_to_master_branch(self, jira_issue):

        response = requests.request(
            "GET",
            urljoin(self.JIRA_URL,
                    "/rest/api/2/issue/{0}/transitions".format(
                        jira_issue)),
            headers=self.HEADERS,
            auth=self.AUTH
        )
        json_o = json.loads(response.text)

        if 'transitions' not in json_o:
            print([jira_issue, 'not found'])
            return

        transition_id = None
        for item in json_o['transitions']:
            if item['name'].upper() == 'IN MASTER REPOSITORY':
                transition_id = item['id']

        if not transition_id:
            print([jira_issue, 'in master branch'])
            return

        payload = json.dumps({
            "transition": {
                "id": transition_id
            }})
        response = requests.request(
            "POST",
            urljoin(self.JIRA_URL,
                    "/rest/api/2/issue/{0}/transitions".format(
                        jira_issue)),
            data=payload,
            headers=self.HEADERS,
            auth=self.AUTH
        )
        print([jira_issue, 'move jira_issue in master branch',
               response.text])


class FreshService(GitHubConfig):
    def check_if_release_exist(self, jira_project_release_name):

        url = "https://support.atrihub.io/itil/releases/filter/new_my_open?format=json&page=1"

        payload = ""
        headers = {
            'Authorization': 'Basic {0}=='.format(self.SB_FRESH_SERVICE)
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json_o = json.loads(response.text)
        for release in json_o:
            if release['subject'] == jira_project_release_name:
                return self.get_url_relese(release['display_id'])

        return False

    def get_url_relese(self, id):
        url = "https://support.atrihub.io/itil/releases/{0}".format(id)
        print(url)
        return url

    def create_release(self, jira_project_release_name, content,
                       sub_category="EDC"):
        if self.check_if_release_exist(jira_project_release_name):
            return

        url = "https://support.atrihub.io/itil/releases.json"
        start_date = date.today()
        end_date = start_date + timedelta(days=3)
        payload = json.dumps({
            "itil_release": {
                "subject": jira_project_release_name,
                "category": "ATRI SDLC",
                "sub_category": sub_category,
                "description": content,
                "planned_start_date": start_date.strftime(
                    "%Y-%m-%dT00:00:00-09:00"),
                "planned_end_date": end_date.strftime(
                    "%Y-%m-%dT00:00:00-09:00")
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic {0}=='.format(self.SB_FRESH_SERVICE)
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        json_o = json.loads(response.text)
        return self.get_url_relese(json_o['item']['itil_release']['display_id'])


class Master():
    def main(self, repository,
             description,
             feature_version,
             feature_master,
             jira_project_release_name,
             git_hub_release_tag,
             target_commitish,
             sub_category,
             plugin_repository=[]):
        # Github
        github_api_o = GitHubAPI()
        print(['clone and get GITHUB info ...'])
        res = github_api_o.run(repository=repository,
                               feature_version=feature_version,
                               feature_master=feature_master)

        finds_unique = res['finds_unique']
        log_file = res['log_file']
        project_name_l = list(set([x.split('-')[0] for x in finds_unique]))

        # Jira
        jira_api_o = JiraAPI()
        print(['get projects ...'])
        project_ids = jira_api_o.get_project_ids()
        print(['create version ...'])
        jira_version = jira_api_o.create_version(project_name_l,
                                                 project_ids,
                                                 jira_project_release_name,
                                                 log_file)
        print(['link Jira to fixVersion ...'])
        for jira_issue in list(set(finds_unique)):
            jira_api_o.link_jira_to_version(jira_issue,
                                            jira_project_release_name)
            jira_api_o.transition_to_master_branch(jira_issue)
        log_jira_issue = jira_api_o.append_summary_log(finds_unique,
                                                       log_file)

        # get the JIRA issues
        print(['Create Release In JIRA  ... '])
        if len(jira_version) > 0:
            # create one only if there is at lease 1 release
            output_relase_str = github_api_o.get_release_note(
                jira_version=jira_version,
                log_jira_issue=log_jira_issue,
                repository=repository,
                log_file=log_file,
                git_hub_release_tag=git_hub_release_tag,
                description=description,
                plugin_repository=plugin_repository)

            github_api_o.create_release(
                repository=repository,
                git_hub_release_tag=git_hub_release_tag,
                body=output_relase_str,
                target_commitish=target_commitish)
        else:
            print("release not created")

        # FreshService
        print(['Create FreshService Release  ... '])
        description_list = [description, ]
        plugin_repository.append(repository)
        for plugin_repository_name in plugin_repository:
            description_list.append(
                "https://github.com/atrihub/{0}/releases/tag/{1}".format(
                    plugin_repository_name, git_hub_release_tag))

        FreshService().create_release(
            jira_project_release_name=jira_project_release_name,
            content="\n".join(description_list),
            sub_category=sub_category)
        # webbrowser.open("file://" + log_file)

    def run_centralservice(self):
        repository = 'centralservice'
        description = """
        Migrate to Django 3.2 
        """
        v_number = "1.3.0"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        jira_project_release_name = "centralservice " + v_number
        git_hub_release_tag = 'v.' + v_number

        self.main(repository=repository,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  description=description,
                  target_commitish='main_django_3_2',
                  sub_category='EDC')

    def run_trc_pad(self):
        repository = 'TRC_PAD'
        description = """
- SLQ 
"""
        v_number = "1.19.2"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        jira_project_release_name = "APT " + v_number
        git_hub_release_tag = 'v.' + v_number

        self.main(repository=repository,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  description=description,
                  target_commitish='main_django_3_2',
                  sub_category='TRC-PAD')

    def run_trc_pad_devops(self):
        repository = 'TRC_PAD_devops'
        description = """
Cogstate - Scoring - AWS Batch Job
    """
        v_number = "v.0.9.6"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        jira_project_release_name = "trcpad_devops " + v_number
        git_hub_release_tag = 'v.' + v_number

        self.main(repository=repository,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  description=description,
                  target_commitish='master',
                  sub_category='TRC-PAD')

    def run_srs(self):
        repository = 'TRC_PAD_SRS'
        description = """
- AlzMatch Community LIVE - Bug fix
"""
        v_number = "1.13.2"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        feature_master = "v_1.13.1"
        jira_project_release_name = "srs " + v_number
        git_hub_release_tag = 'v.' + v_number

        self.main(repository=repository,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  description=description,
                  target_commitish='main_django_3_2',
                  sub_category='TRC-PAD')

    def run_edc(self):
        repository_list = (
            'EDC',
            # 'edc_config',
            # "edc-plugin-msvr",
            # "edc-plugin-image-pipeline",
            # "edc-plugin-data-pipeline",
            # 'edc-meddra',
            # 'edc_plugin_sae_report',
            # 'edc_plugin_casebook',
            # 'edc-bdd',
        )
        description = """
- PHI Redacted
- DATADIC bug fixing - allow "_"
- Improve tests
"""
        v_number = "1.64.4"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        # feature_master = "v_1.63.2"
        jira_project_release_name = "edc " + v_number
        git_hub_release_tag = 'v.' + v_number

        for repository in repository_list:
            plugin_repository = []
            if repository == 'EDC':
                plugin_repository = [r for r in repository_list if
                                     r != repository]
            print([repository, plugin_repository])
            self.main(repository=repository,
                      plugin_repository=plugin_repository,
                      description=description,
                      feature_version=feature_version,
                      feature_master=feature_master,
                      git_hub_release_tag=git_hub_release_tag,
                      jira_project_release_name=jira_project_release_name,
                      target_commitish='main_django_3_2',
                      sub_category='EDC')

    def run_lims(self):
        description = """
- Data Lake
- Dashboard
"""
        v_number = "0.14.1"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        feature_master = "v_0.14.0"
        jira_project_release_name = "lims " + v_number
        git_hub_release_tag = 'v.' + v_number
        self.main(repository='LIMS',
                  description=description,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  target_commitish='main_django_3_2',
                  sub_category='LIMS')

    def run_atri_study_payments(self):
        description = """
- ADD Permission 
"""
        v_number = "0.3.0"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        jira_project_release_name = "Study Payments " + v_number
        git_hub_release_tag = 'v.' + v_number
        self.main(repository='atri-study-payments',
                  description=description,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  target_commitish='main_django_3_2',
                  sub_category='atri-study-payments')
        
    def run_tdd(self):
        repository = 'TDD-Tutorial'
        description = """
- SLQ 
"""
        v_number = "1.19.2"
        feature_version = "v_" + v_number
        feature_master = "main_django_3_2_deployment"
        jira_project_release_name = "APT " + v_number
        git_hub_release_tag = 'v.' + v_number

        self.main(repository=repository,
                  feature_version=feature_version,
                  feature_master=feature_master,
                  git_hub_release_tag=git_hub_release_tag,
                  jira_project_release_name=jira_project_release_name,
                  description=description,
                  target_commitish='main_django_3_2',
                  sub_category='TDD-Tutorial')    

if __name__ == "__main__":
    # execute only if run as a script
    master = Master()
    #master.run_edc()
    # master.run_lims()
    # master.run_centralservice()
    #master.run_trc_pad()
    # master.run_trc_pad_devops()
    # master.run_srs()
    # master.run_trc_pad_devops()
    # master.run_atri_study_payments()
    master.run_tdd()