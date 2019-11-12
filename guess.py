from guesslang import Guess
from database import database, Post
import progressbar

guess = Guess()

def main():
    cnt = 0
    workset = database.session.query(Post).filter(Post.solution_language.is_(None),
                                                  Post.solution_code.isnot(None)).all()
    for i in progressbar.progressbar(workset):
        text = i.solution_code

        language = "(GUESS)" + guess.language_name(text)
        i.solution_language = language
        cnt += 1
        if cnt % 100 == 0:
            database.session.commit()


if __name__ == "__main__":
    main()