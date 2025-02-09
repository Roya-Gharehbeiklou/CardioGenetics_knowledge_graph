# NextGen Knowledge Graph Explorer - Quick Start

## Setup & Run

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download & process data**:
   ```bash
   python scripts/download_data.py
   python scripts/process_data.py
   ```

4. **Run application**:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run
   ```

5. Visit `http://localhost:5000`

## Common Issues

- Port in use? Run on different port: `flask run -p 5001`
- Module not found? Check virtual environment is activated
