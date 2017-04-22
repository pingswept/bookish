from flask import Flask, render_template, request
import json
import requests
import tablib
bookish = Flask(__name__, static_url_path='/static')

DATAFILE = "books.csv"

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
        image_html_list = ['<a href="/books/' + isbn + '"><img src="/static/img/' + isbn + '-S.jpg"></a>' for isbn in dataset['ISBN13']]
        dataset.insert_col(0, image_html_list, header='Cover Image')
    return render_template('index.html', table = dataset.html)

@bookish.route("/books/<isbn>")
def book_detail(isbn):
    data = tablib.Dataset()
    with open(DATAFILE) as f:
        data.csv = f.read()
    print data.headers
    row = data[u'ISBN13'].index(isbn)
    book = data[row]
    return render_template('book.html', title = book[0], author = book[1], isbn = book[3], review = book[12])

@bookish.route("/add_review", methods=['GET', 'POST'])
def add_review():
    data = tablib.Dataset()    
    with open(DATAFILE, 'r') as f:
        data.csv = f.read()
    row = data[u'ISBN13'].index(request.form['isbn'])
    data[row] = data[row][0:12] + (request.form['review'],)
    # still need to save back to file
    with open(DATAFILE, 'wb') as f:
        f.writelines(data.csv)
        f.close()
    return "I tried, okay? I tried.", 204


def book_found(book_data, isbn):
    key = 'ISBN:' + isbn
    if key in book_data:
        return True
    else:
        return False

def check_google_books(isbn):
    r = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + request.form['isbn'])
    print('Checking Google Books by ISBN-13')
    print(r.status_code)
    book_data = json.loads(r.text)
    d = book_data['items'][0]['volumeInfo']

    try:
        author = d['authors'][0]
    except KeyError:
        author = ''

    try:
        publisher = d['publisher']
    except KeyError:
        publisher = ''

    try:
        pages = str(d['pageCount'])
    except KeyError:
        pages = ''

    try:
        pub_date = d['publishedDate']
    except KeyError:
        pub_date = 'unknown'

    data_list = [
        d['title'],
        author,
        isbn,
        isbn,
        publisher,
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

def check_open_library(isbn):
    r = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + isbn + "&jscmd=data&format=json")
    print('Checking Open Library by ISBN-13')
    print(r.status_code)
    book_data = json.loads(r.text)
    try:
        d = book_data['ISBN:' + isbn]
    except KeyError:
        print('Book not found in Open Library')
        data_list = ''
        return data_list

    try:
        author = d['authors'][0]['name']
    except KeyError:
        author = ''
    try:
        author = d['by_statement']
    except KeyError:
        author = ''

    try:
        publisher = d['publishers'][0]['name']
    except KeyError:
        publisher = ''

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
        request.form['isbn'],
        request.form['isbn'],
        publisher,
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
    if(data_list == ''):
        data_list = check_google_books(request.form['isbn'])
    csv_list = [commify(x) for x in data_list]
    result = ",".join(str(elem) for elem in csv_list)
    print(result)
    with open(DATAFILE, 'r') as f:
        lines = f.readlines()
    lines.insert(1, result)
    with open(DATAFILE, 'w') as f:
        f.writelines(lines)
        f.close()
    img = '<img src="http://covers.openlibrary.org/b/isbn/' + request.form['isbn'] + '-S.jpg">'
    table_row = "<td>" + img + "</td><td>" + "</td><td>".join(str(elem) for elem in csv_list) + "</td>"
    return table_row

if __name__ == "__main__":
    bookish.run(host= '0.0.0.0')