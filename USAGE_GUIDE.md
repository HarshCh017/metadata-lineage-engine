# End-to-End Usage and Testing Guide

This guide provides step-by-step instructions on how to use and test the **Metadata Lineage Engine** from the moment you clone the repository.

---

## 1. Clone the Repository

First, pull the source code to your local machine:
```bash
git clone https://github.com/HarshCh017/metadata-lineage-engine.git
cd metadata-lineage-engine
```

---

## 2. Setting Up the Local Environment

We recommend using a Python virtual environment to isolate dependencies.

### Windows (PowerShell)
```powershell
# Create a virtual environment using Python 3.11
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install all required dependencies
pip install -r requirements.txt
```

### macOS / Linux
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Configuring the Application

The application requires a running Neo4j database to store the metadata graph.

1. Copy the example environment file:
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```
2. Open `.env` and verify the Neo4j connection details. 
   *(By default, it assumes Neo4j is running on `localhost:7687` with username `neo4j` and password `password`.)*

---

## 4. Running Neo4j via Docker (Recommended)

If you don't have Neo4j installed locally, the easiest way to start one is using the provided `docker-compose.yml`.

```bash
# Start Neo4j in the background
docker-compose up -d neo4j
```
*Wait a few seconds for the database to initialize.* 
You can access the Neo4j Browser UI at `http://localhost:7474` to view your data visually.

---

## 5. Running the Application API

Start the FastAPI backend server:

```bash
uvicorn lineage_platform.api.app:app --host 0.0.0.0 --port 8000
```
*The API is now running at `http://localhost:8000`.*

---

## 6. Testing the API (End-to-End Test)

Let's test the engine by parsing one of the provided QlikView test scripts.

### Option A: Using curl
Open a new terminal window and run:
```bash
curl -X POST "http://localhost:8000/parse" \
     -H "Content-Type: application/json" \
     -d '{"script_path": "tests/fixtures/qvs/01_simple_load.qvs"}'
```

### Option B: Using PowerShell
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/parse" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"script_path": "tests/fixtures/qvs/01_simple_load.qvs"}'
```

**Expected Result:** You should receive a JSON response indicating success with counts of the tables, fields, and connections processed.

---

## 7. Viewing the Lineage Graph

1. Open your browser and navigate to the Neo4j UI: [http://localhost:7474](http://localhost:7474).
2. Log in with your credentials (default: `neo4j` / `password`).
3. Run the following Cypher query to see everything you just parsed:
   ```cypher
   MATCH (n) RETURN n;
   ```
4. You will visually see the `:QlikScript`, `:QlikTable`, `:Table`, and `:Attribute` nodes connected via lineage edges!

---

## 8. Running the Automated Test Suite

To verify that the entire codebase is functioning correctly without manually hitting endpoints, run the `pytest` suite:

```bash
# Ensure your virtual environment is still activated
pytest tests/
```
*This will execute all unit tests for SQL parsing, field extraction, join logic, and mock graph writes.*

---

## 9. Running with Claude Desktop (Optional MCP Plugin)

If you want Claude to interact with your graph automatically:
1. Ensure the API is running (Step 5).
2. Add the following to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "qlik-lineage": {
         "command": "python",
         "args": ["-m", "lineage_platform.mcp_server"],
         "env": {
           "NEO4J_URI": "bolt://localhost:7687",
           "NEO4J_USERNAME": "neo4j",
           "NEO4J_PASSWORD": "password"
         }
       }
     }
   }
   ```
3. Restart Claude Desktop. You can now ask Claude questions like, *"What tables does the Sales dashboard use?"*
