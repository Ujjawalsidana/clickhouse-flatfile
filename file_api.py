from flask import Blueprint, request, jsonify
import pandas as pd
import os

file_bp = Blueprint('file', __name__, url_prefix='/api/file')

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@file_bp.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    delimiter = request.form.get("delimiter", ",")
    try:
        filepath = os.path.join(UPLOAD_DIR, "uploaded.csv")
        file.save(filepath)
        df = pd.read_csv(filepath, delimiter=delimiter)
        return jsonify({"columns": df.columns.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)})

@file_bp.route("/ingest", methods=["POST"])
def ingest():
    selected = request.json.get("selected_columns", [])
    try:
        df = pd.read_csv(os.path.join(UPLOAD_DIR, "uploaded.csv"), usecols=selected)
        df.to_csv(os.path.join(UPLOAD_DIR, "final.csv"), index=False)
        return jsonify({"count": len(df)})
    except Exception as e:
        return jsonify({"error": str(e)})
