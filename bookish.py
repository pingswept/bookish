from flask import Flask, render_template, request
import requests
import tablib
bookish = Flask(__name__, static_url_path='/static')

dataset = tablib.Dataset()
with open("test.csv") as f:
    dataset.csv = f.read()

@bookish.route('/')
def hello():
    return render_template('index.html')

@bookish.route('/get-book-by-isbn', methods = ['GET', 'POST'])
def get_book():
    r = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + request.form['isbn'] + "&jscmd=data")
    # need to add result to dataset here
    return r.text

@bookish.route("/dataset")
def index():
    return render_template('index.html', table = dataset.html)

if __name__ == "__main__":
    bookish.run()