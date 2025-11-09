# OnDemand Tutor Q&A Agent - Usage Guide

## Quick Start

### 1. Installation
```bash
# Run the automated setup
python setup.py

# Or manually install dependencies
pip install -r requirements.txt
```

### 2. Add Course Materials
Place your Network Security course materials in the `data/course_materials/` directory:
- **Supported formats**: PDF, DOCX, TXT, MD
- **Examples**: lecture slides, textbooks, notes, assignments

### 3. Run the Application
```bash
python main.py
```

This will open a web interface in your browser (usually at `http://localhost:8501`)

## Using the Web Interface

### Initial Setup
1. Click **"Initialize System"** in the sidebar
2. Click **"Setup Knowledge Base"** to process your course materials
3. Wait for the system to process and index your documents

### Asking Questions
1. Type your Network Security question in the main text area
2. Adjust the number of sources to use (1-10)
3. Click **"Ask Question"**
4. Review the answer and source references

### Features
- **Source References**: Every answer includes citations for academic integrity
- **Chat History**: View your recent questions and answers
- **System Stats**: Monitor the knowledge base status
- **Similarity Scores**: See how relevant each source is to your question

## Example Questions

Try these sample questions to test the system:

- "What is a firewall and how does it work?"
- "Explain the difference between symmetric and asymmetric encryption"
- "What are the main types of network security threats?"
- "How does a VPN protect network communications?"
- "Describe the principles of defense in depth"

## File Structure

```
project1/
├── main.py                 # Application entry point
├── setup.py               # Automated setup script
├── requirements.txt       # Python dependencies
├── README.md             # Project overview
├── USAGE_GUIDE.md        # This file
│
├── src/                  # Source code
│   ├── qa_pipeline.py    # Main orchestration logic
│   ├── models/           # GPT4All integration
│   ├── embeddings/       # Sentence Transformers
│   ├── database/         # Chroma vector database
│   ├── utils/            # Document processing
│   └── ui/               # Streamlit interface
│
├── data/                 # Data storage
│   ├── course_materials/ # Place your files here
│   └── processed/        # Generated embeddings and database
│
├── config/               # Configuration settings
├── tests/                # Test scripts
└── models/              # Downloaded AI models
```

## System Architecture

The OnDemand Tutor Q&A Agent uses a sophisticated pipeline:

1. **Document Processing**: Extracts text from PDFs, DOCX, TXT, and MD files
2. **Text Chunking**: Splits documents into manageable pieces with overlap
3. **Vector Embeddings**: Uses Sentence Transformers to create semantic vectors
4. **Vector Storage**: Stores embeddings in Chroma database for fast retrieval
5. **Similarity Search**: Finds most relevant content for user questions
6. **Answer Generation**: Uses GPT4All to generate context-aware responses
7. **Source Attribution**: Provides academic references for transparency

## Privacy and Security

✅ **Fully Offline**: No data leaves your computer
✅ **Local Processing**: All AI models run locally
✅ **No Internet Required**: Works completely offline after initial setup
✅ **Privacy First**: No data collection or external API calls

## Troubleshooting

### Common Issues

**"No documents found"**
- Ensure course materials are in `data/course_materials/`
- Check file formats (PDF, DOCX, TXT, MD only)
- Run "Setup Knowledge Base" after adding files

**"Model download failed"**
- Ensure stable internet connection for initial setup
- Check available disk space (models can be several GB)
- Try running setup again

**"Slow responses"**
- Normal for first run (model loading)
- Large knowledge bases take longer to process
- Consider reducing number of sources

**"Poor quality answers"**
- Check if relevant materials are in knowledge base
- Try rephrasing your question
- Ensure course materials cover the topic

### Performance Tips

1. **Optimize Knowledge Base**: Only include relevant course materials
2. **Manage File Sizes**: Large PDFs may slow processing
3. **Clear Chat History**: Periodically clear to improve performance
4. **Restart System**: Restart if experiencing memory issues

## Testing

Run the test script to verify everything is working:

```bash
python tests/test_pipeline.py
```

This will:
- Test all system components
- Create sample content if needed
- Verify Q&A functionality
- Report any issues

## Advanced Configuration

Edit `config/settings.py` to customize:

- **Chunk Size**: Adjust text chunking parameters
- **Model Selection**: Change AI models (if available)
- **Database Settings**: Modify vector database configuration
- **UI Preferences**: Customize interface settings

## Academic Integrity

This tool is designed to **support learning**, not replace it:

✅ **Appropriate Use**:
- Understanding complex concepts
- Finding relevant course materials
- Reviewing key topics
- Preparing for exams

❌ **Inappropriate Use**:
- Direct copying for assignments
- Avoiding reading course materials
- Replacing critical thinking
- Academic dishonesty

**Always cite sources** and use this tool as a study aid, not a replacement for engaging with course materials directly.

## Support

For issues or questions:
1. Check this usage guide
2. Run the test script for diagnostics
3. Review error messages in the interface
4. Ensure all dependencies are installed correctly

The system is designed to be self-contained and work reliably offline once properly set up.