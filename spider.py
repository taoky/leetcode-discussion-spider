import requests

class LeetcodeSession():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.graphql = "https://leetcode.com/graphql"
        self.client = requests.Session()

    def login(self):
        login_url = "https://leetcode.com/accounts/login/"
        get_login_page = self.client.get(login_url)
        csrf_token = self.client.cookies["csrftoken"]
        login_request = self.client.post(login_url, 
                            {
                                "csrfmiddlewaretoken": csrf_token,
                                "login": self.username,
                                "password": self.password,
                                "next": "/",
                            }, headers=
                            {
                                "referer": login_url,
                            }
                        )
        print("Login Response code: ", login_request.status_code)
        if login_request.status_code != 200:
            print("LOGIN ERROR. Server returns: ", login_request.text)
            exit(-1)

    def get_all_problems(self):
        all_api = "https://leetcode.com/api/problems/all/"
        problem_list = self.client.get(all_api).json()
        problem_list = problem_list["stat_status_pairs"]
        problem_list = [(i["stat"]["question_id"], i["stat"]["question__title_slug"]) for i in problem_list]
        # print(problem_list)
        return problem_list

    def get_problem_discussion(self, problem):
        print("Querying problem " + problem[1])
        discussion = self.client.post(self.graphql, json={
            "operationName": "questionTopicsList",
            "variables": {"questionId": problem[0], "first": 9999999},
            "query": 
                """
                    query questionTopicsList($questionId: String!, $orderBy: TopicSortingOption, $skip: Int, $query: String, $first: Int!, $tags: [String!]) {
                        questionTopicsList(questionId: $questionId, orderBy: $orderBy, skip: $skip, query: $query, first: $first, tags: $tags) {
                            ...TopicsList
                        }
                    }

                    fragment TopicsList on TopicConnection {
                        totalNum
                        edges {
                            node {
                                id
                                title
                                viewCount
                                tags {
                                    name
                                }
                                post {
                                    id
                                }
                            }
                        }
                    }

                """
        }, headers={
            "Referer": "https://leetcode.com/problems/" + problem[1] + "/discuss/",
            "x-csrftoken": self.client.cookies["csrftoken"]
        })
        data = discussion.json()
        data = [{
                    "questionId": problem[0],
                    "topicId": i["node"]["id"],
                    "title": i["node"]["title"],
                    "viewCount": i["node"]["viewCount"],
                    "tags": i["node"]["tags"],
                    "post": i["node"]["post"]["id"]
                } for i in data["data"]["questionTopicsList"]["edges"]]
        print(data)

def main():
    ls = LeetcodeSession(USERNAME, PASSWORD)
    ls.login()
    plist = ls.get_all_problems()
    ls.get_problem_discussion(plist[0])
    for i in plist:
        pass

if __name__ == "__main__":
    try:
        from config import *
    except ModuleNotFoundError:
        print("Please copy config_example.py to config.py, and modify that according to your Leetcode account.")
        exit(-1)
    main()