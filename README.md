# DocuMind AI — Intelligent Document Processing & Risk Detection

DocuMind AI is an AI-powered document processing and risk detection platform designed to automate invoice processing and improve financial document verification.

The application extracts important information from uploaded invoices, validates invoice data, detects duplicate records, compares invoices with purchase orders, identifies unusual transactions using machine learning, and provides intelligent document search and AI-powered question answering.

## Features

### 1. Intelligent Document Processing
- Upload PDF and supported document files.
- Extract document text using PyMuPDF.
- Automatically extract important invoice information.
- Store processed invoice records in MySQL.

### 2. Invoice Validation
- Identify missing invoice information.
- Validate important invoice fields.
- Assign risk levels based on validation results.

### 3. Duplicate Invoice Detection
- Identify previously uploaded invoices.
- Prevent duplicate invoice records from being stored.

### 4. Purchase Order Matching
- Compare invoice amounts with purchase order amounts.
- Detect amount mismatches.
- Identify unknown purchase order references.
- Highlight potential financial risks.

### 5. Machine Learning Anomaly Detection
- Uses the Isolation Forest algorithm.
- Identifies unusual invoice amounts.
- Analyzes invoices stored in the database.
- Displays anomaly scores and detection results.
- Handles insufficient data safely.

### 6. Semantic Invoice Search
- Search using invoice numbers.
- Search using vendor names.
- Search using purchase order numbers.
- Retrieve relevant invoices using semantic similarity.
- Powered by Sentence Transformers and FAISS.

### 7. AI-Powered Document Q&A
- Ask questions about uploaded invoices.
- Retrieve relevant document information.
- Generate document-grounded answers using Gemini AI.

### 8. Interactive Dashboard
- View total uploaded invoices.
- Monitor HIGH, MEDIUM and LOW risk invoices.
- View invoice information.
- Access document processing and AI features.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Database | MySQL |
| ORM | SQLAlchemy |
| Document Processing | PyMuPDF |
| Data Processing | Pandas |
| Machine Learning | Scikit-learn |
| ML Algorithm | Isolation Forest |
| Semantic Search | Sentence Transformers, FAISS |
| Generative AI | Google Gemini AI |
| Frontend | HTML, CSS, JavaScript |
| API Testing | Swagger UI |

## Project Structure

```text
DocuMind-AI/
│
├── app/
│   ├── database/
│   │   ├── connection.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── invoice.py
│   │   └── purchase_order.py
│   │
│   ├── routers/
│   │   ├── rag.py
│   │   └── search.py
│   │
│   ├── schemas/
│   │   ├── rag.py
│   │   └── search.py
│   │
│   ├── services/
│   │   ├── semantic_search/
│   │   │   ├── engine.py
│   │   │   └── indexer.py
│   │   │
│   │   ├── anomaly_detector.py
│   │   ├── document_processor.py
│   │   ├── duplicate_detector.py
│   │   ├── invoice_extractor.py
│   │   ├── invoice_validator.py
│   │   ├── po_matcher.py
│   │   └── rag_service.py
│   │
│   └── utils/
│
├── data/
│   ├── ml/
│   ├── processed/
│   └── uploads/
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
│
├── main.py
├── requirements.txt
├── .gitignore
├── sample_invoice.txt
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.13
- MySQL 8
- Git
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/mohamud007/DocuMind-AI.git
```

```bash
cd DocuMind-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

For Windows:

```bash
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root.

Configure the following according to the application's database and Gemini configuration:

- MySQL database connection details.
- Google Gemini API key.

Use the exact environment variable names expected by the application source code.

**Important:** Never upload your `.env` file or API keys to GitHub.

### 6. Start the Application

```bash
python -m uvicorn main:app --reload
```

### 7. Access the Application

| Service | URL |
|---|---|
| Frontend | http://127.0.0.1:8000 |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check application health |
| GET | `/invoices` | Retrieve invoice records |
| GET | `/risk-summary` | Retrieve invoice risk summary |
| POST | `/recalculate-risks` | Recalculate invoice risks |
| POST | `/documents/upload` | Upload and process documents |
| GET | `/anomalies` | Run ML anomaly detection |

Semantic search and AI question-answering endpoints are also available in Swagger documentation.

## Machine Learning

DocuMind AI uses the Isolation Forest algorithm from Scikit-learn to identify unusual invoice amounts.

The model:
1. Retrieves invoice records from the database.
2. Extracts invoice amounts.
3. Trains an Isolation Forest model on the available records.
4. Identifies unusual amounts.
5. Returns anomaly scores and classifications.

The system requires a minimum of five invoice records before running the current ML analysis to avoid presenting potentially misleading results with very small datasets.

## Testing

The project includes test scripts for:

- Database connectivity.
- Database indexing.
- Duplicate detection.
- Document extraction.
- Invoice extraction.
- Invoice validation.
- Purchase order matching.
- Gemini integration.
- Semantic search.

Core application functionality has also been tested through the frontend and API documentation.

## Future Improvements

- Cloud deployment.
- Advanced financial fraud detection.
- Support for additional document formats.
- Improved machine learning models.
- User authentication and role-based access control.
- Automated document processing workflows.
