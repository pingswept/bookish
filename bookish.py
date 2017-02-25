from flask import Flask, render_template
bookish = Flask(__name__, static_url_path='/static')

@bookish.route("/")
def test():
    return "Hello World!"

@bookish.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)

if __name__ == "__main__":
    bookish.run()