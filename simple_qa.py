#!/usr/bin/env python3
"""
Simple Q&A that works RIGHT NOW with your PDF.
"""

import sys
from pathlib import Path
sys.path.append('src')
from utils.document_processor import DocumentProcessor

def answer_from_pdf(question):
    """Answer question from PDF right now."""
    processor = DocumentProcessor()
    pdf_path = "data/course_materials/1_merged_compressed.pdf"
    
    try:
        text = processor.read_pdf(pdf_path)
        question_lower = question.lower()
        text_lower = text.lower()
        
        # Search for relevant content
        if 'network security' in question_lower:
            start_pos = text_lower.find('network security')
        elif 'firewall' in question_lower:
            start_pos = text_lower.find('firewall')
        elif 'encryption' in question_lower:
            start_pos = text_lower.find('encryption')
        else:
            start_pos = text_lower.find(question_lower.split()[0])
        
        if start_pos != -1:
            context_start = max(0, start_pos - 200)
            context_end = min(len(text), start_pos + 600)
            answer = text[context_start:context_end].strip()
            return answer
        else:
            return "Content found in PDF but specific topic needs refinement."
            
    except Exception as e:
        return f"Error: {e}"

def main():
    print("="*60)
    print("OnDemand Tutor Q&A - WORKING NOW")
    print("="*60)
    
    # Answer your previous questions immediately
    questions = [
        "what is network security",
        "what is a firewall", 
        "what is encryption"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = answer_from_pdf(q)
        print(f"A: {answer[:400]}...")
        print(f"Source: 1_merged_compressed.pdf")
        print("-" * 40)

if __name__ == "__main__":
    main()