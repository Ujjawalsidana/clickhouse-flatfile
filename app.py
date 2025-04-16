from flask import Flask, render_template, request, jsonify
from api import register_blueprints  # Import the function from api/__init__.py
from api.clickhouse_api import clickhouse_bp  # Blueprint for ClickHouse API
import clickhouse_connect  # Updated import for clickhouse-connect
import pandas as pd
from clickhouse_driver import Client
app = Flask(__name__)

# Register all API routes
register_blueprints(app)

# Main route to render the UI
@app.route("/")
def index():
    return render_template("index.html")

# Route to fetch tables from ClickHouse
@app.route("/api/tables", methods=["POST"])
def get_tables():
    data = request.get_json()
    
    # Create a ClickHouse client connection
    client = clickhouse_connect.get_client(
        host=data["host"],
        port=data["port"],
        username=data["user"],
        password=data["token"],
        database=data["db"]
    )
    
    try:
        # Execute the query to show tables
        result = client.query("SHOW TABLES")
        
        # Extract table names from the result
        tables = [row[0] for row in result.result_rows]
        
        return jsonify({"tables": tables})  # Return the tables as a JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch columns from a specific table
@app.route("/api/columns", methods=["POST"])
def get_columns():
    data = request.get_json()
    
    # Create a ClickHouse client connection
    client = clickhouse_connect.get_client(
        host=data["host"],
        port=data["port"],
        username=data["user"],
        password=data["token"],
        database=data["db"]
    )
    
    try:
        # Execute the query to show columns of a specific table
        query = f"DESCRIBE TABLE {data['table']}"
        result = client.query(query)
        
        # Extract column names from the result
        columns = [row[0] for row in result.result_rows]
        
        return jsonify({"columns": columns})  # Return the columns as a JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to start ingestion (this is where you will integrate the ingestion process)
@app.route("/api/ingest", methods=["POST"])
def start_ingestion():
    data = request.get_json()
    if not data["columns"]:
        return jsonify({"error": "No columns selected for ingestion"}), 400

    # Create a ClickHouse client connection
    client = clickhouse_connect.get_client(
        host=data["host"],
        port=data["port"],
        username=data["user"],
        password=data["token"],
        database=data["db"]
    )
    
    try:
        # Build the query to fetch the selected columns from the selected table
        selected_columns = ",".join(data["columns"])
        query = f"SELECT {selected_columns} FROM {data['table']}"
        result = client.query(query)
        
        # Here, you would handle data ingestion (write to a file, etc.)
        # For example, save the result to a CSV file
        import csv
        file_path = "ingested_data.csv"
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(selected_columns.split(","))
            writer.writerows(result.result_rows)
        
        # Return success message with file path
        return jsonify({"file": file_path, "count": len(result.result_rows)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/ingest-flatfile', methods=['POST'])
def get_clickhouse_client():
    # Replace these values with your actual config or fetch them from the frontend if needed
    return Client(
        host='gq1tcm25t9.asia-southeast1.gcp.clickhouse.cloud',
        port='8443',  # or 8443 for HTTPS, depending on your setup
        user='default',
        password='Oy1n.fZoaVFVF',
        database='default'
    )
def ingest_flatfile():
    file = request.files['file']
    if file:
        df = pd.read_csv(file)
        client = get_clickhouse_client()  # You likely already have this function
        client.insert_dataframe('default.sample_data', df)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'No file received'}), 400
@app.route('/preview-flatfile', methods=['POST'])
def preview_flatfile():
    file = request.files['file']
    if file:
        df = pd.read_csv(file)
        preview = df.head().to_string()
        return jsonify({'preview': preview})
    return jsonify({'preview': 'No file uploaded'})

if __name__ == "__main__":
    app.run(debug=True)
