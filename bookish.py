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
    return render_template('index.html', table = dataset.html)

@bookish.route('/get-book-by-isbn', methods = ['GET', 'POST'])
def get_book():
    r = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + request.form['isbn'] + "&jscmd=data&format=json")
    book_data = json.loads(r.text)
    d = book_data['ISBN:' + request.form['isbn']]
    data_list = ['', d['title'], d['by_statement'], '', '', d['identifiers']['isbn_13'][0][3:], d['identifiers']['isbn_13'][0],'','', d['publishers'][0]['name'], '', ''.join(n for n in d['pagination'] if n.isdigit()), d['publish_date'], '', '', 'owned', '', '\n']
    csv_list = [commify(x) for x in data_list]
    result = ",".join(str(elem) for elem in csv_list)
    print result
    with open(DATAFILE, 'r') as f:
        lines = f.readlines()
    lines.insert(1, result)
    with open(DATAFILE, 'w') as f:
        f.writelines(lines)
    return result

if __name__ == "__main__":
    bookish.run()