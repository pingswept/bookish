from flask import Flask, render_template, request
import json
import requests
import tablib
bookish = Flask(__name__, static_url_path='/static')

DATAFILE = "test.csv"

def commify(some_letters):
	if ',' in some_letters:
		return '"' + some_letters + '"'
	else:
		return some_letters

@bookish.route("/")
def index():
    dataset = tablib.Dataset()
    with open(DATAFILE) as f:
        dataset.csv = f.read()
        image_html_list = ['<img src="/static/img/' + isbn + '-S.jpg">' for isbn in dataset['ISBN13']]
        dataset.insert_col(0, image_html_list, header='Cover Image')
    return render_template('index.html', table = dataset.html)

#r = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + request.form['isbn'])

def check_open_library(isbn):
    r = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + isbn + "&jscmd=data&format=json")
    print('Checking by ISBN-13')
    print r.status_code
    if((r.status_code != 200) or (len(r.text) < 5)):
        # This branch of code might be broken. No books with invalid ISBN13 but valid ISBN10 available.
        print('Nothing found via ISBN-13')
        print('Checking by ISBN-10')
        r = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + isbn[3:] + "&jscmd=data&format=json")
        isbn = isbn[3:]
    book_data = json.loads(r.text)
    d = book_data['ISBN:' + isbn]

    try:
        author = d['authors'][0]['name']
    except KeyError:
        author = ''
    try:
        author = d['by_statement']
    except KeyError:
        author = ''

    try:
        pages = ''.join(n for n in d['pagination'] if n.isdigit())
    except KeyError:
        pages = ''

    try:
        pages = str(d['number_of_pages'])
    except KeyError:
        pages = ''

    try:
        pub_date = d['publish_date']
    except KeyError:
        pub_date = 'unknown'

    data_list = [
        d['title'],
        author,
        request.form['isbn'][3:],
        request.form['isbn'],
        d['publishers'][0]['name'],
        '',
        pages,
        pub_date,
        '',
        '',
        'owned',
        '',
        '\n'
    ]
    return data_list

@bookish.route('/get-book-by-isbn', methods = ['GET', 'POST'])
def get_book():
    data_list = check_open_library(request.form['isbn'])
    csv_list = [commify(x) for x in data_list]
    result = ",".join(str(elem) for elem in csv_list)
    print result
    with open(DATAFILE, 'r') as f:
        lines = f.readlines()
    lines.insert(1, result)
    with open(DATAFILE, 'w') as f:
        f.writelines(lines)
        f.close()
    return result

if __name__ == "__main__":
    bookish.run()