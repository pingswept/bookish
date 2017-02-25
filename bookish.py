from flask import Flask, render_template
import requests
bookish = Flask(__name__, static_url_path='/static')

@bookish.route('/')
def hello():
    return render_template('index.html')

@bookish.route('/get-book-by-isbn', methods = ['GET', 'POST'])
def get_book():
    r = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:0451526538")
    return r.text

if __name__ == "__main__":
    bookish.run()