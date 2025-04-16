async function fetchTables() {
  const payload = {
      host: "gq1tcm25t9.asia-southeast1.gcp.clickhouse.cloud",
      port: "8443",
      db: "default",
      user: "default",
      token: "X950pmjKk4~E6"
  };

  const response = await fetch("/api/tables", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
  });

  const data = await response.json();
  console.log("Available Tables: ", data.tables);
}
function uploadFile() {
  const fileInput = document.getElementById('csv-file');
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  fetch('/preview-flatfile', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("preview").innerHTML = "<pre>" + data.preview + "</pre>";
      document.getElementById("ingest-btn").classList.remove("hidden");
    });
}

function showConfigSection(source) {
    document.querySelectorAll(".config").forEach(el => el.classList.add("hidden"));
    if (source === "clickhouse") {
      document.getElementById("clickhouse-config").classList.remove("hidden");
    } else if (source === "flatfile") {
      document.getElementById("flatfile-config").classList.remove("hidden");
    }
  }
  
  document.getElementById("source").addEventListener("change", function () {
    showConfigSection(this.value);
  });
  
  async function fetchTables() {
    const payload = {
      host: document.getElementById("ch-host").value,
      port: document.getElementById("ch-port").value,
      db: document.getElementById("ch-db").value,
      user: document.getElementById("ch-user").value,
      token: document.getElementById("ch-token").value,
    };
  
    const response = await fetch("/api/tables", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
  
    const data = await response.json();
    const tableSelect = document.getElementById("ch-table");
    tableSelect.innerHTML = "";
  
    if (data.tables) {
      data.tables.forEach(table => {
        const option = document.createElement("option");
        option.value = table;
        option.text = table;
        tableSelect.appendChild(option);
      });
    } else {
      alert("Error fetching tables: " + data.error);
    }
  }
  
  async function fetchColumns() {
    const payload = {
      host: document.getElementById("ch-host").value,
      port: document.getElementById("ch-port").value,
      user: document.getElementById("ch-user").value,
      token: document.getElementById("ch-token").value,
      db: document.getElementById("ch-db").value,
      table: document.getElementById("ch-table").value,
  
    };
  
    const response = await fetch("/api/columns", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
  
    const data = await response.json();
    const columnDiv = document.getElementById("ch-columns");
    columnDiv.innerHTML = "";
  
    if (data.columns) {
      data.columns.forEach(col => {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "columns";
        checkbox.value = col;
        checkbox.checked = true;
  
        const label = document.createElement("label");
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(col));
  
        columnDiv.appendChild(label);
        columnDiv.appendChild(document.createElement("br"));
      });
    } else {
      alert("Error fetching columns: " + data.error);
    }
  }
  
  async function startIngestion() {
    const source = document.getElementById("source").value;
    const statusDiv = document.getElementById("status");
    statusDiv.innerText = "Starting ingestion...";
  
    if (source === "clickhouse") {
      const selectedColumns = [...document.querySelectorAll("#ch-columns input[type='checkbox']:checked")].map(cb => cb.value);
  
      const payload = {
        host: document.getElementById("ch-host").value,
        port: document.getElementById("ch-port").value || "8443",
        db: document.getElementById("ch-db").value,
        user: document.getElementById("ch-user").value,
        token: document.getElementById("ch-token").value,
        table: document.getElementById("ch-table").value,
        columns: selectedColumns
      };
  
      const response = await fetch("/api/ingest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
  
      const data = await response.json();
      if (data.file) {
        statusDiv.innerText = `Ingested ${data.count} records! File saved at: ${data.file}`;
      } else {
        statusDiv.innerText = `Error: ${data.error}`;
      }
  
    } else if (source === "flatfile") {
      const fileInput = document.getElementById("csv-file");
      const file = fileInput.files[0];
      if (!file) {
        statusDiv.innerText = "Please upload a CSV file first.";
        return;
      }
  
      const formData = new FormData();
      formData.append("file", file);
      formData.append("host", document.getElementById("ch-host").value);
      formData.append("port", document.getElementById("ch-port").value || "8443");
      formData.append("database", document.getElementById("ch-db").value);
      formData.append("user", document.getElementById("ch-user").value);
      formData.append("token", document.getElementById("ch-token").value);
      formData.append("table", document.getElementById("ch-table").value);
  
      try {
        const response = await fetch("/ingest-flatfile", {
          method: "POST",
          body: formData
        });
  
        const data = await response.json();
        if (data.status === "success") {
          statusDiv.innerText = `Ingested ${data.message}`;
        } else {
          statusDiv.innerText = `Error: ${data.message}`;
        }
      } catch (error) {
        statusDiv.innerText = `Error: ${error.message}`;
      }
    } else {
      statusDiv.innerText = "Please select a valid source.";
    }
  }
   