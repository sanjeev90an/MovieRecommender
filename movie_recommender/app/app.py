from flask.app import Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run("127.0.0.1", "9090", debug=True)