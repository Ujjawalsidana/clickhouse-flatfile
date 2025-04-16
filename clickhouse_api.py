from flask import Blueprint, request, jsonify
import pandas as pd
from clickhouse_connect import get_client

clickhouse_bp = Blueprint("clickhouse_bp", __name__)

# Utility function to create a ClickHouse client connection
from flask import Blueprint, request, jsonify
import pandas as pd
from clickhouse_connect import get_client

@clickhouse_bp .route("/ingest", methods=["POST"])
# utils.py (or inside clickhouse_api.py)


def get_clickhouse_client(data):
    return get_client(
        host=data.get("host"),
        port=data.get("port"),
        username=data.get("user"),
        password=data.get("token"),
        database=data.get("db")
    )

def ingest_from_clickhouse():
    data = request.json
    try:
        # Validate inputs
        if "table" not in data or not data["table"]:
            return jsonify({"error": "Table name is missing"}), 400
        if "columns" not in data or not data["columns"]:
            return jsonify({"error": "No columns provided"}), 400

        client = get_clickhouse_client(data)

        table_name = data["table"]
        columns_list = data["columns"]
        columns = ",".join([f"`{col}`" for col in columns_list])  # quote columns

        query = f"SELECT {columns} FROM `{table_name}`"
        print("Executing query:", query)

        df = client.query_df(query)

        output_file = f"uploads/{table_name}_from_clickhouse.csv"
        df.to_csv(output_file, index=False)

        return jsonify({"count": len(df), "file": output_file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
