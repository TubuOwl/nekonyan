from flask import Flask, jsonify, render_template, request
from scraper import scrape_nekopoi_all, scrape_nekopoi_detail

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape")
def scrape_home():
    return jsonify(scrape_nekopoi_all(10))

@app.route("/detail")
def detail():
    link = request.args.get("link")
    if not link:
        return jsonify({"error": "link parameter required"}), 400
    return jsonify(scrape_nekopoi_detail(link))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
