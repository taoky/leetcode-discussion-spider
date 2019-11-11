from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///leetcode-discussion.db')
Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    
    questionId = Column(Integer, primary_key=True)
    topicId = Column(Integer, primary_key=True)
    title = Column(String)
    viewCount = Column(Integer)
    tags = Column(String)  # as sqlite doesn't support array type, here is a workaround. `tags` just stores things like "["java", "python"]", etc.
    post = Column(Integer)

class Post(Base):
    __tablename__ = 'posts'

    parent = Column(Integer)
    id = Column(Integer, primary_key=True)
    content = Column(String)
    voteCount = Column(Integer)
    creationDate = Column(Integer)
    updationDate = Column(Integer)
    author = Column(String)
    authorReputation = Column(Integer)
    solution_language = Column(String)
    solution_code = Column(String)
    questionId = Column(Integer)  # not for lab requirement, but for less network requests

Base.metadata.create_all(engine)

class Database():
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

database = Database()

def save_discussions(topics):
    for i in topics:
        if not database.session.query(Topic).filter_by(questionId=i["questionId"], topicId=i["topicId"]).first():
            topic = Topic(questionId=i["questionId"],
                        topicId=i["topicId"],
                        title=i["title"],
                        viewCount=i["viewCount"],
                        tags=repr(i["tags"]),
                        post=i["post"])
            database.session.add(topic)
    database.session.commit()

def save_posts(posts, questionId):
    for i in posts:
        if not database.session.query(Post).filter_by(id=i["id"]).first():
            post = Post(parent=i["parent"],
                        id=i["id"],
                        content=i["content"],
                        voteCount=i["voteCount"],
                        creationDate=i["creationDate"],
                        updationDate=i["updationDate"],
                        author=i["author"],
                        authorReputation=i["authorReputation"],
                        solution_language=None,
                        solution_code=None,
                        questionId=questionId)
            database.session.add(post)
    database.session.commit()

def is_question_done(questionId):
    if database.session.query(Topic).filter_by(questionId=questionId).first() and database.session.query(Post).filter_by(questionId=questionId).first():
        return True
    return False