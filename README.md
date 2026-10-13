# \# KamoBox Backend

# 

# Backend API for the KamoBox self-storage platform.

# 

# \## Tech Stack

# 

# \- Python 3.14

# \- FastAPI

# \- Uvicorn

# \- PostgreSQL (planned)

# 

# \## Development Setup

# 

# \### 1. Create a virtual environment

# 

# ```powershell

# py -3.14 -m venv .venv

# ```

# 

# \### 2. Install dependencies

# 

# ```powershell

# .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

# ```

# 

# \### 3. Run the development server

# 

# ```powershell

# .\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

# ```

# 

# \## API Endpoints

# 

# \- `GET /health` — checks whether the API is running.

# \- `/docs` — interactive API documentation.



