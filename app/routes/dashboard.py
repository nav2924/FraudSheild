import os
from flask import Flask, render_template, jsonify
from app.services.blockchain_logger import verify_chain, LEDGER_PATH

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/verify")
def verify():
    return jsonify(verify_chain(LEDGER_PATH))
