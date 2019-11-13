from database import database, Post, Topic
import json

def main():
    with open("output.json", "w") as f:
        posts = database.session.query(Post).all()
        topics = database.session.query(Topic).all()

        for i in topics:
            res = {
                "questionId": i.questionId,
                "topicId": i.topicId,
                "title": i.title,
                "viewCount": i.viewCount,
                "tags": [item[1:-1] for item in i.tags[1:-1].split(",")],
                "post": i.post
            }
            f.write(json.dumps(res) + "\n")

        for i in posts:
            res = {
                "parent": i.parent,
                "id": i.id, 
                "content": i.content,
                "voteCount": i.voteCount,
                "creationDate": i.creationDate,
                "updationDate": i.updationDate,
                "author": i.author,
                "authorReputation": i.authorReputation,
            }
            if i.solution_code:
                res["solution"] = {
                    "language": i.solution_language,
                    "code": i.solution_code
                }
            f.write(json.dumps(res) + "\n")

if __name__ == "__main__":
    main()