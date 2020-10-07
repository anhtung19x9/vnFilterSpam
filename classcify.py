from pathlib import Path
from psycopg2 import connect
from underthesea import word_tokenize


def read_file(file_path):
    txt = Path(file_path).read_text()
    txt = txt.replace('\n', '')
    txt = txt.replace('.', '')
    process_word(txt)


def process_word(pre_text):
    text = word_tokenize(pre_text)
    process_lower(text)


def process_lower(text):
    text = [x.lower() for x in text]
    clear_hot_word(text)


def clear_hot_word(text):
    hotword = ['có thể', 'nếu', 'vì vậy', 'sau khi', 'thì', 'nếu không', 'trước khi', 'vì thế', 'loại trừ', 'tất cả',
               'là', 'một số', 'những', 'nhưng', 'rõ ràng', 'phần lớn', 'bởi', 'với', 'hầu như', 'với lại',
               'nói chung', 'nên', 'vậy']
    for x in text:
        if x in hotword:
            text.remove(x)
    clear_sign(text)


def clear_sign(text):
    for x in text:
        if len(x) == 1:
            text.remove(x)
    clear_duplicate(text)


def clear_duplicate(text):
    text = list(dict.fromkeys(text))
    process_db(text)


def process_db(text):
    db = connect(dbname="token", user="postgres", password="Ecoit@123database", host="118.70.180.97", port="5698")
    cur = db.cursor()

    # Calculator ham and spam score in content
    cur.execute("select * from total")
    number = cur.fetchone()
    number_ham = number[1]
    number_spam = number[2]
    number_total = number[3]

    spam_content = number_spam / number_total
    ham_content = number_ham / number_total
    #print(spam_content)
    #print(ham_content)
    # process token score in spam and ham type
    spam_token = ham_token = 1
    for x in text:
        cur.execute("select * from frequency where word like %s", (x,))
        value = cur.fetchone()
        if not (value is None):
            word_ham = value[1]
            word_spam = value[2]
            word_total = value[3]

            word_spam_score = word_spam/number_spam
            word_ham_score = word_ham/number_ham
            word_total_score = word_total/number_total

            word_spam_token = (spam_content*word_spam_score)/word_total_score
            word_ham_token = (ham_content*word_ham_score)/word_total_score

            if word_spam_token != 0:
                spam_token *= word_spam_token
            if word_ham_token != 0:
                ham_token *= word_ham_token

    total_content = spam_token*spam_content+ham_token*ham_content

    score = (spam_token*spam_content)/total_content

    print(score)
    # sent all changes to database
    db.commit()


if __name__ == '__main__':
    user_input = input("Enter path to file: ")
    read_file(user_input)
