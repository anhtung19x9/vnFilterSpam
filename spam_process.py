import glob
from pathlib import Path
from psycopg2 import connect
from underthesea import word_tokenize


def get_all_file(dic_path):
    file_path = glob.glob(dic_path + "/spam*.txt")
    for x in file_path:
        read_file(x)


def read_file(file_path):
    txt = Path(file_path).read_text(encoding="utf-8")
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

    # process total table for spam and ham numbers
    cur.execute("select spam,total from total")
    number = cur.fetchone()
    number_spam = number[0] + 1
    number_total = number[1] + 1
    cur.execute("update total set spam = %s, total = %s where id =1", (number_spam, number_total))

    # process token table for frequency
    for x in text:
        cur.execute("select * from frequency where word like %s", (x,))
        value = cur.fetchone()
        if value is None:
            cur.execute("insert into frequency values (%s,%s,%s,%s)", (x, 0, 1, 1))
        else:
            token_spam = value[2] + 1
            token_total = value[3] + 1
            cur.execute("update frequency set spam = %s, total = %s where word like %s", (token_spam, token_total, x))

    # sent all changes to database
    db.commit()


if __name__ == '__main__':
    #user_input = input("Enter path to spam files: ")
    read_file("test.txt")
