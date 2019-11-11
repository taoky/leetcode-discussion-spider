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
        problem_list = [i["stat"]["question__title_slug"] for i in problem_list]
        print(problem_list)
        return problem_list

    def get_problem_discussion(self, problem_name):


def main():
    ls = LeetcodeSession(USERNAME, PASSWORD)
    ls.login()
    plist = ls.get_all_problems()
    for i in plist:


if __name__ == "__main__":
    try:
        from config import *
    except ModuleNotFoundError:
        print("Please copy config_example.py to config.py, and modify that according to your Leetcode account.")
        exit(-1)
    main()