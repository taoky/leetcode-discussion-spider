import requests
import math
from database import database, save_discussions, is_question_done, save_posts
import itertools
import time

INF = 2**31 - 1
flatten = itertools.chain.from_iterable

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
        return problem_list

    def get_problem_discussion(self, problem):
        print("Querying problem " + problem[1])
        while True:
            discussion = self.client.post(self.graphql, json={
                "operationName": "questionTopicsList",
                "variables": {"questionId": problem[0], "first": INF},  # FIXME: a dirty hack to graphql pagination
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
                "Referer": "https://leetcode.com/",
                "x-csrftoken": self.client.cookies["csrftoken"]
            })
            if discussion.status_code < 500:
                break
            else:
                time.sleep(1)
        data = discussion.json()
        data = [{
                    "questionId": problem[0],
                    "topicId": i["node"]["id"],
                    "title": i["node"]["title"],
                    "viewCount": i["node"]["viewCount"],
                    "tags": [tag["name"] for tag in i["node"]["tags"]],
                    "post": i["node"]["post"]["id"]
                } for i in data["data"]["questionTopicsList"]["edges"]]
        return data

    def get_discussion_posts(self, topic_id):
        res = []  # FIXME: an ugly impl
        while True:
            parent = self.client.post(self.graphql, json={
                "operationName": "DiscussTopic", 
                "variables": {"topicId": topic_id},
                "query":
                """
                query DiscussTopic($topicId: Int!) {
                    topic(id: $topicId) {
                        topLevelCommentCount
                        post {
                        ...DiscussPost
                        }
                    }
                    }

                    fragment DiscussPost on PostNode {
                        id
                        voteCount
                        content
                        updationDate
                        creationDate
                        author {
                            username
                            profile {
                            reputation
                            }
                        }
                    }
                """
            }, headers={
                "Referer": "https://leetcode.com/",
                "x-csrftoken": self.client.cookies["csrftoken"]
            })
            if parent.status_code < 500:
                break
            else:
                print("`parent` Retrying...")
                time.sleep(1)
        if parent.status_code != 200:
            print("`parent` Response code %d." % parent.status_code)
            print("Server returns: " + parent.text)
            exit(-1)
        parent = parent.json()
        comment_cnt = parent["data"]["topic"]["topLevelCommentCount"]
        parent = parent["data"]["topic"]["post"]
        parent = {
            "parent": -1,
            "id": parent["id"], 
            "content": parent["content"],
            "voteCount": parent["voteCount"],
            "creationDate": parent["creationDate"],
            "updationDate": parent["updationDate"],
            "author": parent["author"]["username"],
            "authorReputation": parent["author"]["profile"]["reputation"],
        }
        res = [parent]
        if (comment_cnt > 0):
            while True:
                comments = self.client.post(self.graphql, json={
                    "operationName": "discussComments", 
                    "variables": {"orderBy": "best", "pageNo": 1, "numPerPage": INF, "topicId": topic_id},
                    "query":
                    """
                    query discussComments($topicId: Int!, $orderBy: String, $pageNo: Int = 1, $numPerPage: Int = 10) {
                        topicComments(topicId: $topicId, orderBy: $orderBy, pageNo: $pageNo, numPerPage: $numPerPage) {
                            data {
                                id
                                post {
                                    ...DiscussPost
                                }
                                numChildren
                            }
                        }
                        }

                        fragment DiscussPost on PostNode {
                            id
                            voteCount
                            content
                            updationDate
                            creationDate
                            author {
                                username
                                profile {
                                reputation
                                }
                            }
                        }
                    """
                }, headers={
                    "Referer": "https://leetcode.com/",
                    "x-csrftoken": self.client.cookies["csrftoken"]
                })
                if comments.status_code < 500:
                    break
                else:
                    print("`comments` Retrying...")
                    time.sleep(1)
            if comments.status_code != 200:
                print("`comments` Response code %d." % comments.status_code)
                print("Server returns: " + comments.text)
                exit(-1)
            comments = comments.json()
            comments = comments["data"]["topicComments"]["data"]
            for i in comments:
                comment = {
                    "parent": parent["id"],
                    "id": i["post"]["id"], 
                    "content": i["post"]["content"],
                    "voteCount": i["post"]["voteCount"],
                    "creationDate": i["post"]["creationDate"],
                    "updationDate": i["post"]["updationDate"],
                    "author": i["post"]["author"]["username"],
                    "authorReputation": i["post"]["author"]["profile"]["reputation"],
                }
                res.append(comment)
                replies_cnt = i["numChildren"]
                if replies_cnt > 0:
                    while True:
                        replies = self.client.post(self.graphql, json={
                            "operationName": "fetchCommentReplies", 
                            "variables": {"commentId": i["id"]},
                            "query":
                            """
                            query fetchCommentReplies($commentId: Int!) {
                                commentReplies(commentId: $commentId) {
                                    id
                                    post {
                                    ...DiscussPost
                                    }

                                }
                                }

                                fragment DiscussPost on PostNode {
                                id
                                voteCount
                                content
                                updationDate
                                creationDate
                                author {
                                    username
                                    profile {
                                    reputation
                                    }
                                }
                                }

                            """
                        }, headers={
                            "Referer": "https://leetcode.com/",
                            "x-csrftoken": self.client.cookies["csrftoken"]
                        })
                        if replies.status_code < 500:
                            break
                        else:
                            print("`replies` Retrying...")
                            time.sleep(1)
                    if replies.status_code != 200:
                        print("`replies` Response code %d." % replies.status_code)
                        print("Server returns: " + replies.text)
                        exit(-1)
                    replies = replies.json()
                    replies = replies["data"]["commentReplies"]
                    for j in replies:
                        reply = {
                            "parent": i["post"]["id"],
                            "id": j["post"]["id"], 
                            "content": j["post"]["content"],
                            "voteCount": j["post"]["voteCount"],
                            "creationDate": j["post"]["creationDate"],
                            "updationDate": j["post"]["updationDate"],
                            "author": j["post"]["author"]["username"],
                            "authorReputation": j["post"]["author"]["profile"]["reputation"],
                        }
                        res.append(reply)

        return res

def main():
    ls = LeetcodeSession(USERNAME, PASSWORD)
    ls.login()
    plist = ls.get_all_problems()

    print("Get %d problems." % len(plist))
    for i in plist:
        if is_question_done(i[0]):
            # if questionId exists
            print("Skipped problem %d." % i[0])
            continue
        print("Getting discussions of problem %d." % i[0])
        discussions = ls.get_problem_discussion(i)
        save_discussions(discussions)
        print("Getting posts of discussions of problem %d." % i[0])
        posts = [ls.get_discussion_posts(i["topicId"]) for i in discussions]
        posts = list(flatten(posts))
        save_posts(posts, i[0])

    database.session.close()

if __name__ == "__main__":
    try:
        from config import *
    except ModuleNotFoundError:
        print("Please copy config_example.py to config.py, and modify that according to your Leetcode account.")
        exit(-1)
    main()