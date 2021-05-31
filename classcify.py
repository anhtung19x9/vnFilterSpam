from pathlib import Path
from psycopg2 import connect
from underthesea import word_tokenize
from gensim.parsing.preprocessing import strip_numeric,strip_non_alphanum

def read_file():
    txt = Path("test.txt").read_text(encoding="utf-8")
    process_word(txt)


def process_word(pre_text):
    pre_text = pre_text.replace('\n', '')
    pre_text = pre_text.replace('.', '')
    return clear_unknown_letter(pre_text)


def clear_unknown_letter(text):
    text = strip_non_alphanum(text)
    text = word_tokenize(text)
    return process_lower(text)


def process_lower(text):
    text = [x.lower() for x in text]
    return clear_hot_word(text)


def clear_hot_word(text):
    hotword = ['có thể', 'nếu', 'vì vậy', 'sau khi', 'thì', 'nếu không', 'trước khi', 'vì thế', 'loại trừ', 'tất cả',
               'là', 'một số', 'những', 'nhưng', 'rõ ràng', 'phần lớn', 'bởi', 'với', 'hầu như', 'với lại',
               'nói chung', 'nên', 'vậy']
    for x in text:
        if x in hotword:
            text.remove(x)
    return clear_sign(text)


def clear_sign(text):
    for x in text:
        if len(x) == 1:
            text.remove(x)
    return clear_duplicate(text)


def clear_duplicate(text):
    text = list(dict.fromkeys(text))
    return process_db(text)


def process_db(text):
    db = connect(dbname="token", user="postgres", password="Ecoit@123database", host="118.70.180.97", port="5698")
    cur = db.cursor()

    cur.execute("select * from total")
    number = cur.fetchone()
    number_ham = number[1]
    number_spam = number[2]
    number_total = number[3]

    spam_content = number_spam / number_total
    ham_content = number_ham / number_total

    # process token score in spam and ham type
    spam_token = ham_token = 1
    for x in text:
        cur.execute("select * from frequency where word like %s", (x,))
        value = cur.fetchone()
        if not (value is None):
            word_ham = value[1]
            word_spam = value[2]
            word_total = value[3]

            word_spam_score = word_spam+1/number_spam+1
            word_ham_score = word_ham+1/number_ham+1
            word_total_score = word_total/number_total

            word_spam_token = (spam_content*word_spam_score)/word_total_score
            word_ham_token = (ham_content*word_ham_score)/word_total_score

            spam_token *= word_spam_token
            ham_token *= word_ham_token

    total_content = spam_token*spam_content+ham_token*ham_content
    score = (spam_token*spam_content)/total_content
    print(score)
    if score > 0.5:
        return 1
    return 0
    # sent all changes to database
    db.commit()


if __name__ == '__main__':
    #user_input = input("Enter path to file: ")
    read_file()
