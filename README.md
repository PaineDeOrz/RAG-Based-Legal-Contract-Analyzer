\# Rental Contract Analyzer



\[Streamlit App](https://static.streamlit.io/badges/using-streamlit\_app\_badge.svg)



AI-powered rental contract analysis (German/English). Upload your rental agreement to get rent price, deposit, termination rules, safety score instantly.



\## Features



\- Multilingual: Works with German (Kaution, Kündigungsfrist) + English contracts

\- Key Extraction: Rent euro450, Deposit euro600, 2-month notice, etc.

\- Risk Scoring: Flags missing clauses + high-risk terms

\- Semantic Search: Find "parking fees" or "house rules" instantly

\- Streamlit UI: Clean, interactive rental table





\## Quick Start



```bash

\# 1. Clone \& install

git clone https://github.com/PaineDeOrz/RAG-Based-Legal-Contract-Analyzer

cd RAG-Based-Legal-Contract-Analyzer

pip install -r requirements.txt



\# 2. Add your Gemini API key

export GEMINI\_API\_KEY="your-key-here"



\# 3. Add your contract

mkdir -p data/pdfs

cp your-rental-contract.pdf data/pdfs/



\# 4. Run

streamlit run src/app.py

```



\## Source \& Structure



Adapted from Policy-Compliance-Checker repo (original README in Policy-Compliance-Checker folder):



\- Forked \& specialized for rental contracts

\- No extra files added - just modified for rental use case

\- Multilingual TF-IDF (DE/EN legal terms)

\- Rental-specific rules (10 clauses: rent, deposit, termination)

\- Production-ready (.gitignore, requirements.txt)



Files modified:

\- compliance\_rules.py → Rental rules (DE/EN keywords)

\- compliance\_checker.py → Rental table + safety scoring

\- pdf\_processor.py → Real PDFs only, multilingual search

\- app.py → Rental-focused Streamlit UI

\- config.py → Production settings



\## Tech Stack



\- Frontend: Streamlit

\- AI: Google Gemini 2.5 Flash (multilingual)

\- Search: scikit-learn TF-IDF + Cosine Similarity

\- PDF: pdfplumber

\- Storage: Local vector store (privacy-focused)



\## Repo Structure

├── requirements.txt # Dependencies

├── .gitignore # No PDFs/API keys

├── README.md # This file

├──Policy-Compliance-Cheacker/

&#x20;    ├── app.py # Streamlit UI

&#x20;    ├── compliance\_checker.py # Rental analysis engine

&#x20;    ├── compliance\_rules.py # DE/EN rental rules (10 clauses)

&#x20;    ├── pdf\_processor.py # Multilingual PDF → TF-IDF

&#x20;    ├── config.py # Settings



