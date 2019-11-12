from database import database, Post
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
        'go': 'Go',
        'sh': 'Bash',
        'py': 'Python',
        'js': 'JavaScript',
        'c': 'C'
    })

def get_from_language_keyword(content):
    content = content.lower()
    
    for keyword in keyword_dict:
        if keyword in content:
            return keyword_dict[keyword]
    return None

def main():
    cnt = 0
    for i in progressbar.progressbar(database.session.query(Post).filter_by(solution_language=None).all()):
        content = markdown.markdown(
            i.content.encode('utf-8').decode('unicode-escape'),
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
                if len(j.text) > len(max_len_element.text):
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
            else:
                guess_dict = guess.scores(max_len_element.text)
                guess_dict = OrderedDict(sorted(guess_dict.items(), key=lambda x: x[1], reverse=True))
                # print(j, guess_dict)

                guess_result = list(guess_dict.items())[0]
                guess_index = 0
                while guess_result[0] in stoplist:
                    guess_index += 1
                    guess_result = list(guess_dict.items())[guess_index]
                
                language = guess_result[0]
                if guess_result[1] < 0.9:
                    # not so confidient
                    key_lang = get_from_language_keyword(max_len_element.text)
                    if key_lang:
                        language = key_lang
            # print(j.text, language)
            i.solution_language = language
            i.solution_code = j.text
            cnt += 1
            if cnt % 100 == 0:
                database.session.commit()


if __name__ == "__main__":
    main()