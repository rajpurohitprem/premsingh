from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory("web", path)

@app.route('/')
def root():
    return send_from_directory("web", "picker.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
