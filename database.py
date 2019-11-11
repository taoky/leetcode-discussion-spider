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

    parent = Column(Integer, primary_key=True)
    id = Column(Integer, primary_key=True)
    content = Column(String)
    voteCount = Column(Integer)
    creationDate = Column(Integer)
    updationDate = Column(Integer)
    author = Column(String)
    authorReputation = Column(Integer)
    solution_language = Column(String)
    solution_code = Column(String)

class Database():
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

database = Database()