from database import database, Post, Topic
import markdown
import lxml.html
import progressbar
from guesslang import Guess  # pip install git+https://github.com/yoeo/guesslang.git
from collections import OrderedDict

guess = Guess()

stoplist = ["Objective-C", "Markdown", "HTML", "Erlang", "Perl", "CSS"]
keyword_dict = OrderedDict({
    'kotlin': 'Kotlin',
    'python': 'Python',
    'rust': 'Rust',
    'scala': 'Scala',
    'swift': 'Swift',
    'javascript': 'JavaScript',
    'java': 'Java',
    'ruby': 'Ruby',
    'php': 'PHP',
    'sql': 'SQL',
    'c#': 'C#',
    'c++': 'C++',
    'cpp': 'C++',
    'cs': 'C#',
    'golang': 'Go',
    'go': 'Go',
    'sh': 'Bash',
    'shell': 'Bash',
    'bash': 'Bash',
    'py': 'Python',
    'js': 'JavaScript',
    'c': 'C'
})


def get_from_language_keyword(content):
    content = content.lower()

    for keyword in keyword_dict:
        if keyword in content.split(" "):
            return keyword_dict[keyword]
    return None


def pure_guess(element):
    language = None
    content_list = element.text.split(" ")
    for i in content_list:
        language = get_from_language_keyword(i)
        if language:
            return language
    if not language:
        # returns language
        guess_dict = guess.scores(element.text)
        guess_dict = OrderedDict(sorted(guess_dict.items(), key=lambda x: x[1], reverse=True))
        # print(j, guess_dict)

        guess_result = list(guess_dict.items())[0]
        guess_index = 0
        while guess_result[0] in stoplist:
            guess_index += 1
            guess_result = list(guess_dict.items())[guess_index]

        language = guess_result[0]
    return language


def main():
    cnt = 0
    workset = database.session.query(Post).filter(Post.solution_language.is_(None)).all()
    for i in progressbar.progressbar(workset):
        content = i.content.encode('utf-8').decode('unicode-escape')
        if len(content) == 0:
            continue
        content = markdown.markdown(
            content,
            extensions=['fenced_code']
        )
        root = lxml.html.fromstring(content)
        code_blocks = root.xpath('//pre/code')
        if not code_blocks:
            continue
        else:
            max_len_element = code_blocks[0]
            for j in code_blocks:
                if j.text is None:
                    # a bug???
                    continue
                if max_len_element.text is None or len(j.text) > len(max_len_element.text):
                    max_len_element = j

            if max_len_element.text is None:
                # wtf?
                print("Post %d meets a strange error." % i.id)
                continue

            if len(max_len_element.classes) != 0:
                for klass in max_len_element.classes:
                    # Classes class does not support indexing...
                    if klass.lower() in keyword_dict:
                        klass = keyword_dict[klass.lower()]
                    language = klass
                    break
            elif database.session.query(Topic).filter_by(post=i.id).count():
                topic = database.session.query(Topic).filter_by(post=i.id).one()
                tags = topic.tags[1:-1].split(",")
                language = None
                for j in tags:
                    l = get_from_language_keyword(j)
                    if l:
                        language = l
                        break
                if not language:
                    title = topic.title.split(" ")
                    for j in title:
                        l = get_from_language_keyword(j)
                        if l:
                            language = l
                            break
                if not language:
                    language = pure_guess(max_len_element)
            else:
                language = pure_guess(max_len_element)
            # print(j.text, language)
            i.solution_language = language
            i.solution_code = max_len_element.text
            cnt += 1
            if cnt % 100 == 0:
                database.session.commit()


if __name__ == "__main__":
    main()
