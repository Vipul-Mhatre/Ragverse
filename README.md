# Ragverse

Production-grade enterprise Retrieval-Augmented Generation (RAG) scaffold with:
- Next.js frontend
- FastAPI backend
- FAISS-enabled hybrid retrieval
- JWT + RBAC-first authorization
- Explainable response contracts
- Dockerized deployment assets

## Quick start

### 1) Generate sample enterprise dataset
```bash
python backend/scripts/generate_sample_dataset.py
```

### 2) Run backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3) Run frontend
```bash
cd frontend
npm install
npm run dev
```

### 4) Test backend
```bash
cd backend
pytest
```
