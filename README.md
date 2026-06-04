# Bulls Eye Backend

Python Flask backend for Bulls-eye.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

The API runs at `http://localhost:5000`.

## Tests

```bash
python -m pytest tests
```

## Environment

Use `.env.example` as the reference for required backend variables.
