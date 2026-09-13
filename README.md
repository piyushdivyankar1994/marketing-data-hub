# Marketing Data Hub 📊

A full-stack, audit-compliant data platform designed to ingest, transform, normalize, and visualize heterogeneous marketing metrics across multiple delivery formats (**Meta CSV**, **LinkedIn JSON**, and **Google Ads CSV**).

![Architecture Diagram](data/images/CampaignHub.png)

---

## 🌟 Key Features

* **Modular Ingestion Pipeline:** Extensible `IngestionPipeline` driven by schema configuration maps heterogeneous inputs into standard `CampaignMetric` canonical entities.
* **Cross-Column & Currency Transformation:** Built-in `ExchangeRates` repository supports dynamic rate conversions (`EUR` $\rightarrow$ `USD`), nested JSON spend parsing, and micros conversion (`Cost / 1,000,000`).
* **FR-2 & FR-5 Data Quality Diagnostics:** Tracks ingestion health, record failure breakdowns, and generates granular JSON execution reports.
* **NFR-3 Full Traceability:** Dynamic lineage drawer in the UI maps any displayed aggregate metric back to its source delivery file and exact schema transformation rules.
* **Interactive Dashboard:** Dynamic platform filtering, campaign aggregations, automated delivery ID extraction, and UI schema presets.

---
## 🚀 Running the Application

Use the provided `run.sh` script to set up virtual environments, install dependencies, and launch both the backend (FastAPI) and frontend (Vite) servers concurrently.

```bash
# Make the script executable (first time only)
chmod +x run.sh

# Start the full-stack application
./run.sh

```

#### Launch Flags & Options

* **Reset Database on Startup:**
Wipe the SQLite database (`marketing_data.db`) before starting the server:
```bash
./run.sh --reset-db

```



#### Accessing Services

Once started, the application services will be available at:

* **React Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
* **FastAPI Backend Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

*Press `Ctrl + C` in the terminal to stop both backend and frontend servers cleanly.*
