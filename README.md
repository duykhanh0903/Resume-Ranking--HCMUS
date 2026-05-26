# RecruitAI: Automated Resume Screening & Ranking System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.24.0+-FF4B4B.svg?logo=streamlit)
![NLP](https://img.shields.io/badge/NLP-SBERT%20%7C%20Llama%203.1-orange.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

RecruitAI is a practical NLP system designed to solve real-world recruitment challenges by automating the initial candidate screening process. The system performs semantic analysis to rank resumes against job descriptions, ensuring a fair, objective, and efficient hiring workflow.

---

## 📌 Project Objective
The objective is to design and document a production-ready system that manages data handling, model development, and ethical responsibility in NLP applications.

## 🏗️ System Architecture
The system follows a modular client-server architecture:
* **Backend (FastAPI):** Encapsulates the core logic including Regex parsing, SBERT scoring, and LLM reasoning.
* **Frontend (Streamlit):** Provides a reactive user interface for recruiters to interact with the analysis results.
* **Data Pipeline:** Manages the flow from raw data ingestion to structured JSON extraction and semantic ranking.

## 🧩 Core Components

### 1. Information Extraction (Parsing & OCR)
* **Multi-format Input:** Extracts text from PDF and DOCX files using `pdfplumber` and `python-docx`.
* **Layout Awareness:** Implements density-based scanning to handle single or double-column CV layouts.
* **Hybrid Validation:** Combines Llama 3.1 for contextual parsing with Regex for high-precision contact info extraction.

### 2. Standard Analyzer (Rule-Based ATS)
* **Scoring Logic:** Calculates an ATS score based on six weighted indicators: Skills (30%), Experience (20%), Formatting (20%), Contact (10%), Summary (10%), and Education (10%).
* **Normalization:** Uses a synonym dictionary to standardize technical terms (e.g., "Node" vs "Node.js").
* **Formatting Check:** Evaluates CV presentation, including spacing, section headers, and bullet points.

### 3. AI Analyzer (Semantic Ranking)
* **Architecture:** Utilizes a fine-tuned Sentence-BERT model to measure semantic similarity.
* **Training & Optimization:** Hyperparameters optimized via Optuna.
* **Ranking Metric:** Employs Spearman Cosine Correlation to ensure high-quality ranking performance.

### 4. Resume Ranking (Admin Dashboard)
* **Decision Support:** Provides a leaderboard for HR admins to visualize and sort candidates based on Standard and AI scores.
* **Dynamic Weighting:** Allows admins to adjust weights for different scoring components based on specific hiring needs.
* **Statistics:** Visualizes recruitment metrics such as Success Rate and average scores.

### 5. Job Search Aggregator
* **Direct Access:** Generates programmatic search queries for major job portals including LinkedIn, Indeed, Naukri, and Foundit.
* **Market Insights:** Provides trending skills and salary benchmarks to help candidates align with market demands.

### 6. Resume Builder (Export to DOCX)
* **Automated Generation:** Converts user input into professionally formatted DOCX resumes using `python-docx`.
* **Memory Management:** Uses `io.BytesIO` for direct data streaming, ensuring fast responses without creating temporary files on the server.

## 📂 Repository Structure
```text
project-root/
├── src/                    # Core source code
│   ├── api/               # FastAPI routers (analyzer, builder, ranking, jobsearch)
│   ├── engine/            # AI Agent (LangGraph + Groq) + SBERT tools
│   ├── pipelines/         # Data processing, training, evaluation, HPO
│   ├── utils/             # Parser, Extractor, Scorer, Supabase client
│   └── ui/                # Streamlit multi-page frontend (app.py)
├── data/                  # Managed by DVC (raw + processed)
├── models/                # Trained SBERT checkpoints (DVC-tracked)
├── configs/               # Job role definitions (JOB_ROLES dict)
├── standards/             # Scoring criteria JSON per role
├── tests/                 # Unit test scaffolding
├── Dockerfile             # Containerization
├── requirements.txt       # Python dependencies
└── README.md              # Setup, inference guide

```

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/duykhanh0903/Resume-Ranking--HCMUS.git
   cd Resume-Ranking--HCMUS
   ```
2. **Inject Required Assets:**
   Extract the downloaded files from the Google Drive link (attached in HCMUS Moodle) directly into the root directory of this project. Ensure the following items are present in the root folder before proceeding:
   * data/ (Sample resumes and processed datasets)
   * models/ (Fine-tuned SBERT model weights)
   * vendor/ (Third-party dependencies/configs)
   * .env (API keys and database credentials)
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Launch the Backend:**
   ```bash
   uvicorn src.api.main:app --reload
   ```
5. **Launch the Frontend:**

   Open a new terminal and run:
   ```bash
   streamlit run src/ui/app.py
   ```

## ⚖️ Ethics & Privacy

The system includes logic to prioritize objective skill matching. Future implementations will integrate PII (Personally Identifiable Information) redaction to anonymize candidate data before processing, reducing demographic bias.