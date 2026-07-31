# IntelliScore AI

An Explainable AI Platform for Automated Essay Evaluation, Writing Improvement,
Academic Integrity Detection, Essay Comparison, and Learning Analytics.

Built as a final-year B.Tech AI & Data Science project, using production
software engineering practices: modular architecture, config-driven secrets,
tested increments per module.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, JWT auth
- **Frontend:** Streamlit
- **ML:** XGBoost, scikit-learn
- **Deep Learning / NLP:** PyTorch, DeBERTa-v3 (transformers), Sentence-Transformers, spaCy, NLTK
- **Documents/OCR:** PyMuPDF, python-docx, pdfplumber, EasyOCR
- **LLM:** LangChain + Google Gemini
- **Vector store:** FAISS
- **Reports:** ReportLab, python-docx

## Project Status

Module 0 (environment & scaffolding) complete. See `docs/` for the module
roadmap as it develops.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt

cp .env.example .env
# then edit .env: set JWT_SECRET_KEY and GEMINI_API_KEY

# Run backend
cd backend && uvicorn app.main:app --reload

# Run frontend (separate terminal)
cd frontend/streamlit_app && streamlit run Home.py
```

## Project Structure

```
backend/app/     FastAPI service — routes, models, schemas, services
frontend/        Streamlit UI
ml/              Framework-agnostic NLP/ML/DL code (no backend/frontend imports)
data/            Raw & processed data (gitignored)
reports/         Report templates and generated output
vectorstore/     FAISS index persistence
config/          Non-secret app configuration
requirements/    base.txt (runtime) / dev.txt (+ testing & linting)
```
