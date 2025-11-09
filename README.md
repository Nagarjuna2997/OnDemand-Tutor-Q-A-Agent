# OnDemand Tutor Q&A Agent

A privacy-focused, secure Q&A system for Network Security courses built with GPT4All, Sentence Transformers, and Chroma vector database.

## Features

- **Privacy-First**: All processing happens locally, no data leaves your machine
- **Offline Capability**: Works without internet connection once set up
- **Semantic Search**: Uses Sentence Transformers for accurate content retrieval
- **Source References**: Provides transparency with source material citations
- **Academic Integrity**: Maintains proper attribution for all responses

## Architecture

- **LLM Framework**: GPT4All with Gemma model for local inference
- **Embeddings**: Sentence Transformers (multi-qa-MiniLM-L6-cos-v1)
- **Vector Database**: Chroma for efficient similarity search
- **Interface**: Streamlit web application

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place course materials in `data/course_materials/`

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

```
project1/
├── src/
│   ├── models/          # GPT4All integration
│   ├── database/        # Chroma vector database
│   ├── embeddings/      # Sentence Transformers
│   ├── ui/             # Streamlit interface
│   └── utils/          # Utilities and document processing
├── data/
│   ├── course_materials/  # Raw course content
│   └── processed/        # Processed embeddings and database
├── config/             # Configuration settings
├── tests/              # Unit tests
└── models/            # Downloaded AI models
```# OnDemand-Tutor-Q-A-Agent
