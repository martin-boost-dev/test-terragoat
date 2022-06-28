"""
Record the creation of a checks run.  Run within the venv with `poetry run`.

Needs an installed github app.
"""

import json
from pathlib import Path

import requests
from boostsec.testing.wire_mock import WireMock, WireMockServer
from github import Github, GithubIntegration
from github.MainClass import DEFAULT_BASE_URL

# ENVIRONMENT SETUP
github_app_id = 155688
installation_id = 21045661
private_key = (
    Path("/Users/martinroy/work/martin-dev-boost.2021-12-01.private-key.pem")
    .read_text()
    .strip()
)
test_repo = "martin-boost-dev/test-repo"
pull_request_id = 1


# START RECORDER
server: WireMock = WireMockServer().run(
    container_name="scm-integrations-wire-mock-recording"
)

requests.post(
    f"{server.admin_url}/recordings/start",
    json={
        "targetBaseUrl": DEFAULT_BASE_URL,
        "captureHeaders": {
            "Authorization": {},
            "Accept": {},
        },
    },
)

# OPEN GIT REPO
integration = GithubIntegration(github_app_id, private_key, base_url=server.url)
auth_obj = integration.get_access_token(installation_id)  # Token good for 1 hour
github_client = Github(auth_obj.token, base_url=server.url)
repo = github_client.get_repo(test_repo)

# HACK TO OVERRIDE URL RETURNED BY GITHUB
repo._url.value = repo._url.value.replace("https://api.github.com", server.url)

issue = repo.get_issue(pull_request_id)
issue._url.value = issue._url.value.replace("https://api.github.com", server.url)

print(issue.url)
print(issue)
result = issue.create_comment(
    """\
### :warning:  3 New Security Finding~~s~~
The latest commit contains 3 new security issue~~s~~.

| **Findings**
| ------------
| **My Rule Title** <br/> Rule description
| https://github.com/martin-boost-dev/test-repo/blob/c000c45b6f7658abdd5f0457675671921540f2a2/README.md#L3
| **My Rule Title2** <br/> Rule description
| https://github.com/martin-boost-dev/test-repo/blob/c000c45b6f7658abdd5f0457675671921540f2a2/README.md#L2-L3

[Not an issue?](https://docs.boostsecurity.io/faq/index.html#how-can-i-ignore-a-finding) Ignore it by adding a comment on the line with just the word `noboost`.

---

### :rocket: 2 New Security Fix~~s~~
You just committed 2 security fix~~s~~. :sunglasses: Keep up the great work!

<details>
<summary>:dart:Take a look at what issues you fixed.</summary>

| **Findings**
| ------------
| **My Rule Title** <br/> Rule description
| https://github.com/martin-boost-dev/test-repo/blob/c000c45b6f7658abdd5f0457675671921540f2a2/README.md
| **My Rule Title2** <br/> Rule description
| https://github.com/martin-boost-dev/test-repo/blob/c000c45b6f7658abdd5f0457675671921540f2a2/READMEMISS.md#L2-L3

</details>

[Not an issue?](https://docs.boostsecurity.io/faq/index.html#how-can-i-ignore-a-finding) Ignore it by adding a comment on the line with just the word `noboost`.
"""  # noqa: E501
)
print(result)

result = requests.post(f"{server.admin_url}/recordings/stop")
# SHOW RESULT IN TERMINAL
print(json.dumps(result.json(), indent=2))

# RESULT:
"""
{
  "mappings": [
    {
      "id": "9eceb5ad-01e7-45b5-9275-1b1c07893c62",
      "name": "app_installations_21045661_access_tokens",
      "request": {
        "url": "/app/installations/21045661/access_tokens",
        "method": "POST",
        "headers": {
          "Authorization": {
            "equalTo": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2NDM2NDExMzgsImV4cCI6MTY0MzY0MTE5OCwiaXNzIjoxNTU2ODh9.Qgs_EwQZiu0AR_FXzZ4H3AATQ_eEnAZp0xRpAk-6fG2f4ItVID1T9cDlgqal6qbA8rXLRBknFWXyoMzN1qijOvmkeaAQVNF1AgVirFZN8xppcGQx9QhE0INaYPXV0v6gz38JLVriO6uZ-qybEM4sAxLK-F31kzsjZgm2Hh8xPoZyN4XfiJgw7b3SQl8QPtD_H8wXzfsR2zk5gKCk87yO12SOCfxSZbuPB2Zrcn1Bz4bzjmLnsT0kR_aoYeBUtROKAOevS6onOQ0ER742iZ08L8NFJ5sTEfwrmt5Bph3A-eH0TS68IUakNUrWFlkaiGMgIyw4dUsYZ85A7O0ccUGi1Q"
          },
          "Accept": {
            "equalTo": "application/vnd.github.machine-man-preview+json"
          }
        },
        "bodyPatterns": [
          {
            "equalToJson": "{}",
            "ignoreArrayOrder": true,
            "ignoreExtraElements": true
          }
        ]
      },
      "response": {
        "status": 201,
        "body": "{\"token\":\"ghs_37NP5el7eY8q3TM88O8GwIJ1njCFlQ4SW1gg\",\"expires_at\":\"2022-01-31T15:58:58Z\",\"permissions\":{\"members\":\"read\",\"checks\":\"write\",\"contents\":\"write\",\"issues\":\"write\",\"metadata\":\"read\",\"pull_requests\":\"write\"},\"repository_selection\":\"all\"}",
        "headers": {
          "Server": "GitHub.com",
          "Date": "Mon, 31 Jan 2022 14:58:58 GMT",
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "public, max-age=60, s-maxage=60",
          "Vary": [
            "Accept",
            "Accept-Encoding, Accept, X-Requested-With"
          ],
          "ETag": "\"002a06064410a93f01cb9145dedc20d1a210d60fabd51f5997c91c7b8ec007a3\"",
          "X-GitHub-Media-Type": "github.v3; param=machine-man-preview; format=json",
          "Strict-Transport-Security": "max-age=31536000; includeSubdomains; preload",
          "X-Frame-Options": "deny",
          "X-Content-Type-Options": "nosniff",
          "X-XSS-Protection": "0",
          "Referrer-Policy": "origin-when-cross-origin, strict-origin-when-cross-origin",
          "Content-Security-Policy": "default-src 'none'",
          "X-GitHub-Request-Id": "E8DB:5BF9:DC3F1A:223B0A7:61F7F932"
        }
      },
      "uuid": "9eceb5ad-01e7-45b5-9275-1b1c07893c62",
      "persistent": true
    },
    {
      "id": "c6cf9747-2f63-4ff4-ac23-2912e195a92a",
      "name": "repos_martin-boost-dev_test-repo",
      "request": {
        "url": "/repos/martin-boost-dev/test-repo",
        "method": "GET",
        "headers": {
          "Authorization": {
            "equalTo": "token ghs_37NP5el7eY8q3TM88O8GwIJ1njCFlQ4SW1gg"
          },
          "Accept": {
            "equalTo": "*/*"
          }
        }
      },
      "response": {
        "status": 200,
        "body": "{\"id\":433492562,\"node_id\":\"R_kgDOGdaSUg\",\"name\":\"test-repo\",\"full_name\":\"martin-boost-dev/test-repo\",\"private\":true,\"owner\":{\"login\":\"martin-boost-dev\",\"id\":95301622,\"node_id\":\"O_kgDOBa4v9g\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/95301622?v=4\",\"gravatar_id\":\"\",\"url\":\"https://api.github.com/users/martin-boost-dev\",\"html_url\":\"https://github.com/martin-boost-dev\",\"followers_url\":\"https://api.github.com/users/martin-boost-dev/followers\",\"following_url\":\"https://api.github.com/users/martin-boost-dev/following{/other_user}\",\"gists_url\":\"https://api.github.com/users/martin-boost-dev/gists{/gist_id}\",\"starred_url\":\"https://api.github.com/users/martin-boost-dev/starred{/owner}{/repo}\",\"subscriptions_url\":\"https://api.github.com/users/martin-boost-dev/subscriptions\",\"organizations_url\":\"https://api.github.com/users/martin-boost-dev/orgs\",\"repos_url\":\"https://api.github.com/users/martin-boost-dev/repos\",\"events_url\":\"https://api.github.com/users/martin-boost-dev/events{/privacy}\",\"received_events_url\":\"https://api.github.com/users/martin-boost-dev/received_events\",\"type\":\"Organization\",\"site_admin\":false},\"html_url\":\"https://github.com/martin-boost-dev/test-repo\",\"description\":null,\"fork\":false,\"url\":\"https://api.github.com/repos/martin-boost-dev/test-repo\",\"forks_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/forks\",\"keys_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/keys{/key_id}\",\"collaborators_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/collaborators{/collaborator}\",\"teams_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/teams\",\"hooks_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/hooks\",\"issue_events_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/events{/number}\",\"events_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/events\",\"assignees_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/assignees{/user}\",\"branches_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/branches{/branch}\",\"tags_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/tags\",\"blobs_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/git/blobs{/sha}\",\"git_tags_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/git/tags{/sha}\",\"git_refs_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/git/refs{/sha}\",\"trees_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/git/trees{/sha}\",\"statuses_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/statuses/{sha}\",\"languages_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/languages\",\"stargazers_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/stargazers\",\"contributors_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/contributors\",\"subscribers_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/subscribers\",\"subscription_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/subscription\",\"commits_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/commits{/sha}\",\"git_commits_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/git/commits{/sha}\",\"comments_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/comments{/number}\",\"issue_comment_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/comments{/number}\",\"contents_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/contents/{+path}\",\"compare_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/compare/{base}...{head}\",\"merges_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/merges\",\"archive_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/{archive_format}{/ref}\",\"downloads_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/downloads\",\"issues_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues{/number}\",\"pulls_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/pulls{/number}\",\"milestones_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/milestones{/number}\",\"notifications_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/notifications{?since,all,participating}\",\"labels_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/labels{/name}\",\"releases_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/releases{/id}\",\"deployments_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/deployments\",\"created_at\":\"2021-11-30T15:55:00Z\",\"updated_at\":\"2021-11-30T15:55:00Z\",\"pushed_at\":\"2022-01-31T14:55:02Z\",\"git_url\":\"git://github.com/martin-boost-dev/test-repo.git\",\"ssh_url\":\"git@github.com:martin-boost-dev/test-repo.git\",\"clone_url\":\"https://github.com/martin-boost-dev/test-repo.git\",\"svn_url\":\"https://github.com/martin-boost-dev/test-repo\",\"homepage\":null,\"size\":0,\"stargazers_count\":0,\"watchers_count\":0,\"language\":null,\"has_issues\":true,\"has_projects\":true,\"has_downloads\":true,\"has_wiki\":true,\"has_pages\":false,\"forks_count\":0,\"mirror_url\":null,\"archived\":false,\"disabled\":false,\"open_issues_count\":1,\"license\":null,\"allow_forking\":false,\"is_template\":false,\"topics\":[],\"visibility\":\"private\",\"forks\":0,\"open_issues\":1,\"watchers\":0,\"default_branch\":\"main\",\"permissions\":{\"admin\":false,\"maintain\":false,\"push\":false,\"triage\":false,\"pull\":false},\"temp_clone_token\":\"AWXR2NCVF2OBM4ZWKHG3ITDB675F7AVPNFXHG5DBNRWGC5DJN5XF62LEZYAUCIM5WFUW443UMFWGYYLUNFXW4X3UPFYGLN2JNZ2GKZ3SMF2GS33OJFXHG5DBNRWGC5DJN5XA\",\"allow_squash_merge\":true,\"allow_merge_commit\":true,\"allow_rebase_merge\":true,\"allow_auto_merge\":false,\"delete_branch_on_merge\":false,\"allow_update_branch\":false,\"organization\":{\"login\":\"martin-boost-dev\",\"id\":95301622,\"node_id\":\"O_kgDOBa4v9g\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/95301622?v=4\",\"gravatar_id\":\"\",\"url\":\"https://api.github.com/users/martin-boost-dev\",\"html_url\":\"https://github.com/martin-boost-dev\",\"followers_url\":\"https://api.github.com/users/martin-boost-dev/followers\",\"following_url\":\"https://api.github.com/users/martin-boost-dev/following{/other_user}\",\"gists_url\":\"https://api.github.com/users/martin-boost-dev/gists{/gist_id}\",\"starred_url\":\"https://api.github.com/users/martin-boost-dev/starred{/owner}{/repo}\",\"subscriptions_url\":\"https://api.github.com/users/martin-boost-dev/subscriptions\",\"organizations_url\":\"https://api.github.com/users/martin-boost-dev/orgs\",\"repos_url\":\"https://api.github.com/users/martin-boost-dev/repos\",\"events_url\":\"https://api.github.com/users/martin-boost-dev/events{/privacy}\",\"received_events_url\":\"https://api.github.com/users/martin-boost-dev/received_events\",\"type\":\"Organization\",\"site_admin\":false},\"network_count\":0,\"subscribers_count\":1}",
        "headers": {
          "Server": "GitHub.com",
          "Date": "Mon, 31 Jan 2022 14:58:59 GMT",
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "private, max-age=60, s-maxage=60",
          "Vary": [
            "Accept, Authorization, Cookie, X-GitHub-OTP",
            "Accept-Encoding, Accept, X-Requested-With"
          ],
          "ETag": "W/\"1863887de382fadb041816055bfe2c33dcae5849dadb41fb5da5e283b734742d\"",
          "Last-Modified": "Tue, 30 Nov 2021 15:55:00 GMT",
          "X-GitHub-Media-Type": "github.v3; format=json",
          "X-RateLimit-Limit": "5000",
          "X-RateLimit-Remaining": "4999",
          "X-RateLimit-Reset": "1643644739",
          "X-RateLimit-Used": "1",
          "X-RateLimit-Resource": "core",
          "Strict-Transport-Security": "max-age=31536000; includeSubdomains; preload",
          "X-Frame-Options": "deny",
          "X-Content-Type-Options": "nosniff",
          "X-XSS-Protection": "0",
          "Referrer-Policy": "origin-when-cross-origin, strict-origin-when-cross-origin",
          "Content-Security-Policy": "default-src 'none'",
          "X-GitHub-Request-Id": "E8DD:2D5C:10B51D0:25725EA:61F7F933"
        }
      },
      "uuid": "c6cf9747-2f63-4ff4-ac23-2912e195a92a",
      "persistent": true
    },
    {
      "id": "5eacdf88-ffe5-4d14-90bd-7a4ba9a47de9",
      "name": "repos_martin-boost-dev_test-repo_issues_1",
      "request": {
        "url": "/repos/martin-boost-dev/test-repo/issues/1",
        "method": "GET",
        "headers": {
          "Authorization": {
            "equalTo": "token ghs_37NP5el7eY8q3TM88O8GwIJ1njCFlQ4SW1gg"
          },
          "Accept": {
            "equalTo": "*/*"
          }
        }
      },
      "response": {
        "status": 200,
        "body": "{\"url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1\",\"repository_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo\",\"labels_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/labels{/name}\",\"comments_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/comments\",\"events_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/events\",\"html_url\":\"https://github.com/martin-boost-dev/test-repo/pull/1\",\"id\":1119536183,\"node_id\":\"PR_kwDOGdaSUs4x1954\",\"number\":1,\"title\":\"This is a PR\",\"user\":{\"login\":\"lindycoder\",\"id\":12926519,\"node_id\":\"MDQ6VXNlcjEyOTI2NTE5\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/12926519?v=4\",\"gravatar_id\":\"\",\"url\":\"https://api.github.com/users/lindycoder\",\"html_url\":\"https://github.com/lindycoder\",\"followers_url\":\"https://api.github.com/users/lindycoder/followers\",\"following_url\":\"https://api.github.com/users/lindycoder/following{/other_user}\",\"gists_url\":\"https://api.github.com/users/lindycoder/gists{/gist_id}\",\"starred_url\":\"https://api.github.com/users/lindycoder/starred{/owner}{/repo}\",\"subscriptions_url\":\"https://api.github.com/users/lindycoder/subscriptions\",\"organizations_url\":\"https://api.github.com/users/lindycoder/orgs\",\"repos_url\":\"https://api.github.com/users/lindycoder/repos\",\"events_url\":\"https://api.github.com/users/lindycoder/events{/privacy}\",\"received_events_url\":\"https://api.github.com/users/lindycoder/received_events\",\"type\":\"User\",\"site_admin\":false},\"labels\":[],\"state\":\"open\",\"locked\":false,\"assignee\":null,\"assignees\":[],\"milestone\":null,\"comments\":0,\"created_at\":\"2022-01-31T14:55:02Z\",\"updated_at\":\"2022-01-31T14:55:02Z\",\"closed_at\":null,\"author_association\":\"CONTRIBUTOR\",\"active_lock_reason\":null,\"draft\":false,\"pull_request\":{\"url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/pulls/1\",\"html_url\":\"https://github.com/martin-boost-dev/test-repo/pull/1\",\"diff_url\":\"https://github.com/martin-boost-dev/test-repo/pull/1.diff\",\"patch_url\":\"https://github.com/martin-boost-dev/test-repo/pull/1.patch\",\"merged_at\":null},\"body\":null,\"closed_by\":null,\"reactions\":{\"url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/reactions\",\"total_count\":0,\"+1\":0,\"-1\":0,\"laugh\":0,\"hooray\":0,\"confused\":0,\"heart\":0,\"rocket\":0,\"eyes\":0},\"timeline_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/timeline\",\"performed_via_github_app\":null}",
        "headers": {
          "Server": "GitHub.com",
          "Date": "Mon, 31 Jan 2022 14:58:59 GMT",
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "private, max-age=60, s-maxage=60",
          "Vary": [
            "Accept, Authorization, Cookie, X-GitHub-OTP",
            "Accept-Encoding, Accept, X-Requested-With"
          ],
          "ETag": "W/\"c52eed96dff24e4bcd11447da658151f5f8e62c0568ab26bae605b827e24f981\"",
          "Last-Modified": "Mon, 31 Jan 2022 14:55:02 GMT",
          "X-GitHub-Media-Type": "github.v3; format=json",
          "X-RateLimit-Limit": "5000",
          "X-RateLimit-Remaining": "4998",
          "X-RateLimit-Reset": "1643644739",
          "X-RateLimit-Used": "2",
          "X-RateLimit-Resource": "core",
          "Strict-Transport-Security": "max-age=31536000; includeSubdomains; preload",
          "X-Frame-Options": "deny",
          "X-Content-Type-Options": "nosniff",
          "X-XSS-Protection": "0",
          "Referrer-Policy": "origin-when-cross-origin, strict-origin-when-cross-origin",
          "Content-Security-Policy": "default-src 'none'",
          "X-GitHub-Request-Id": "E8DE:22DB:1A00253:372A31D:61F7F933"
        }
      },
      "uuid": "5eacdf88-ffe5-4d14-90bd-7a4ba9a47de9",
      "persistent": true
    },
    {
      "id": "35c3a47b-1530-4edd-b30f-953a35eaa635",
      "name": "repos_martin-boost-dev_test-repo_issues_1_comments",
      "request": {
        "url": "/repos/martin-boost-dev/test-repo/issues/1/comments",
        "method": "POST",
        "headers": {
          "Authorization": {
            "equalTo": "token ghs_37NP5el7eY8q3TM88O8GwIJ1njCFlQ4SW1gg"
          },
          "Accept": {
            "equalTo": "*/*"
          }
        },
        "bodyPatterns": [
          {
            "equalToJson": "{\"body\": \"HEYYYYY There.\"}",
            "ignoreArrayOrder": true,
            "ignoreExtraElements": true
          }
        ]
      },
      "response": {
        "status": 201,
        "body": "{\"url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/comments/1025842352\",\"html_url\":\"https://github.com/martin-boost-dev/test-repo/pull/1#issuecomment-1025842352\",\"issue_url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/1\",\"id\":1025842352,\"node_id\":\"IC_kwDOGdaSUs49JRyw\",\"user\":{\"login\":\"martin-dev-boost[bot]\",\"id\":95362356,\"node_id\":\"BOT_kgDOBa8dNA\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/12926519?v=4\",\"gravatar_id\":\"\",\"url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D\",\"html_url\":\"https://github.com/apps/martin-dev-boost\",\"followers_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/followers\",\"following_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/following{/other_user}\",\"gists_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/gists{/gist_id}\",\"starred_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/starred{/owner}{/repo}\",\"subscriptions_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/subscriptions\",\"organizations_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/orgs\",\"repos_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/repos\",\"events_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/events{/privacy}\",\"received_events_url\":\"https://api.github.com/users/martin-dev-boost%5Bbot%5D/received_events\",\"type\":\"Bot\",\"site_admin\":false},\"created_at\":\"2022-01-31T14:59:00Z\",\"updated_at\":\"2022-01-31T14:59:00Z\",\"author_association\":\"NONE\",\"body\":\"HEYYYYY There.\",\"reactions\":{\"url\":\"https://api.github.com/repos/martin-boost-dev/test-repo/issues/comments/1025842352/reactions\",\"total_count\":0,\"+1\":0,\"-1\":0,\"laugh\":0,\"hooray\":0,\"confused\":0,\"heart\":0,\"rocket\":0,\"eyes\":0},\"performed_via_github_app\":null}",
        "headers": {
          "Server": "GitHub.com",
          "Date": "Mon, 31 Jan 2022 14:59:00 GMT",
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "private, max-age=60, s-maxage=60",
          "Vary": [
            "Accept, Authorization, Cookie, X-GitHub-OTP",
            "Accept-Encoding, Accept, X-Requested-With"
          ],
          "ETag": "\"672259ebcb99adde48e88f73954d35ccaea31e857c7f5b2dec99f4331fe072ab\"",
          "Location": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/comments/1025842352",
          "X-GitHub-Media-Type": "github.v3; format=json",
          "X-RateLimit-Limit": "5000",
          "X-RateLimit-Remaining": "4997",
          "X-RateLimit-Reset": "1643644739",
          "X-RateLimit-Used": "3",
          "X-RateLimit-Resource": "core",
          "Strict-Transport-Security": "max-age=31536000; includeSubdomains; preload",
          "X-Frame-Options": "deny",
          "X-Content-Type-Options": "nosniff",
          "X-XSS-Protection": "0",
          "Referrer-Policy": "origin-when-cross-origin, strict-origin-when-cross-origin",
          "Content-Security-Policy": "default-src 'none'",
          "X-GitHub-Request-Id": "E8E1:6CD7:191DDB6:363ABED:61F7F933"
        }
      },
      "uuid": "35c3a47b-1530-4edd-b30f-953a35eaa635",
      "persistent": true
    }
  ]
}

"""  # noqa: E501

# GET ISSUE BODY
"""
{
  "url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1",
  "repository_url": "https://api.github.com/repos/martin-boost-dev/test-repo",
  "labels_url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/labels{/name}",
  "comments_url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/comments",
  "events_url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/events",
  "html_url": "https://github.com/martin-boost-dev/test-repo/pull/1",
  "id": 1119536183,
  "node_id": "PR_kwDOGdaSUs4x1954",
  "number": 1,
  "title": "This is a PR",
  "user": {
    "login": "lindycoder",
    "id": 12926519,
    "node_id": "MDQ6VXNlcjEyOTI2NTE5",
    "avatar_url": "https://avatars.githubusercontent.com/u/12926519?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/lindycoder",
    "html_url": "https://github.com/lindycoder",
    "followers_url": "https://api.github.com/users/lindycoder/followers",
    "following_url": "https://api.github.com/users/lindycoder/following{/other_user}",
    "gists_url": "https://api.github.com/users/lindycoder/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/lindycoder/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/lindycoder/subscriptions",
    "organizations_url": "https://api.github.com/users/lindycoder/orgs",
    "repos_url": "https://api.github.com/users/lindycoder/repos",
    "events_url": "https://api.github.com/users/lindycoder/events{/privacy}",
    "received_events_url": "https://api.github.com/users/lindycoder/received_events",
    "type": "User",
    "site_admin": false
  },
  "labels": [],
  "state": "open",
  "locked": false,
  "assignee": null,
  "assignees": [],
  "milestone": null,
  "comments": 0,
  "created_at": "2022-01-31T14:55:02Z",
  "updated_at": "2022-01-31T14:55:02Z",
  "closed_at": null,
  "author_association": "CONTRIBUTOR",
  "active_lock_reason": null,
  "draft": false,
  "pull_request": {
    "url": "https://api.github.com/repos/martin-boost-dev/test-repo/pulls/1",
    "html_url": "https://github.com/martin-boost-dev/test-repo/pull/1",
    "diff_url": "https://github.com/martin-boost-dev/test-repo/pull/1.diff",
    "patch_url": "https://github.com/martin-boost-dev/test-repo/pull/1.patch",
    "merged_at": null
  },
  "body": null,
  "closed_by": null,
  "reactions": {
    "url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/reactions",
    "total_count": 0,
    "+1": 0,
    "-1": 0,
    "laugh": 0,
    "hooray": 0,
    "confused": 0,
    "heart": 0,
    "rocket": 0,
    "eyes": 0
  },
  "timeline_url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1/timeline",
  "performed_via_github_app": null
}
"""  # noqa: E501

# CREATE ISSUE RESPONSE
"""
{
  "url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/comments/1025842352",
  "html_url": "https://github.com/martin-boost-dev/test-repo/pull/1#issuecomment-1025842352",
  "issue_url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/1",
  "id": 1025842352,
  "node_id": "IC_kwDOGdaSUs49JRyw",
  "user": {
    "login": "martin-dev-boost[bot]",
    "id": 95362356,
    "node_id": "BOT_kgDOBa8dNA",
    "avatar_url": "https://avatars.githubusercontent.com/u/12926519?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D",
    "html_url": "https://github.com/apps/martin-dev-boost",
    "followers_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/followers",
    "following_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/following{/other_user}",
    "gists_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/subscriptions",
    "organizations_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/orgs",
    "repos_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/repos",
    "events_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/events{/privacy}",
    "received_events_url": "https://api.github.com/users/martin-dev-boost%5Bbot%5D/received_events",
    "type": "Bot",
    "site_admin": false
  },
  "created_at": "2022-01-31T14:59:00Z",
  "updated_at": "2022-01-31T14:59:00Z",
  "author_association": "NONE",
  "body": "HEYYYYY There.",
  "reactions": {
    "url": "https://api.github.com/repos/martin-boost-dev/test-repo/issues/comments/1025842352/reactions",
    "total_count": 0,
    "+1": 0,
    "-1": 0,
    "laugh": 0,
    "hooray": 0,
    "confused": 0,
    "heart": 0,
    "rocket": 0,
    "eyes": 0
  },
  "performed_via_github_app": null
}
"""  # noqa: E501
