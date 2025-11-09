#!/usr/bin/env python3
"""
Interim Q&A system that works with your PDF RIGHT NOW
while sentence-transformers installs.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from utils.document_processor import DocumentProcessor

class InterimQA:
    """Simple Q&A system using text search until AI components are ready."""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.pdf_path = "data/course_materials/1_merged_compressed.pdf"
        self.pdf_text = None
        self._load_pdf()
    
    def _load_pdf(self):
        """Load and process the PDF."""
        print("Loading your PDF...")
        try:
            self.pdf_text = self.processor.read_pdf(self.pdf_path)
            print(f"✓ Successfully loaded PDF: {len(self.pdf_text)} characters")
            return True
        except Exception as e:
            print(f"✗ Error loading PDF: {e}")
            return False
    
    def answer_question(self, question):
        """Answer question using simple text matching."""
        if not self.pdf_text:
            return "Error: Could not load PDF"
        
        question_lower = question.lower()
        text_lower = self.pdf_text.lower()
        
        # Define search patterns for common questions
        patterns = {
            'network security': ['network security', 'computer network security'],
            'firewall': ['firewall', 'packet filtering'],
            'encryption': ['encryption', 'cryptography', 'cipher'],
            'malware': ['malware', 'virus', 'trojan', 'worm'],
            'authentication': ['authentication', 'identity verification'],
            'intrusion': ['intrusion', 'intrusion detection'],
            'vpn': ['vpn', 'virtual private network'],
            'cia triad': ['confidentiality', 'integrity', 'availability'],
            'attack': ['attack', 'threat', 'vulnerability']
        }
        
        # Find the best matching topic
        best_match = None
        for topic, keywords in patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                best_match = topic
                break
        
        if not best_match:
            # Fallback to first occurrence of any word from question
            words = question_lower.split()
            for word in words:
                if len(word) > 3 and word in text_lower:
                    best_match = word
                    break
        
        if best_match:
            # Find context around the match
            search_terms = patterns.get(best_match, [best_match])
            for term in search_terms:
                start_pos = text_lower.find(term)
                if start_pos != -1:
                    # Extract context
                    context_start = max(0, start_pos - 300)
                    context_end = min(len(self.pdf_text), start_pos + 1200)
                    context = self.pdf_text[context_start:context_end].strip()
                    
                    return {
                        'answer': context,
                        'source': '1_merged_compressed.pdf',
                        'method': 'Text search (interim mode)',
                        'topic': best_match,
                        'status': 'SUCCESS'
                    }
        
        return {
            'answer': f"I found content in your PDF but couldn't locate specific information about '{question}'. The PDF contains {len(self.pdf_text)} characters of Network Security content. Try asking about: network security, firewall, encryption, malware, authentication, or VPN.",
            'source': '1_merged_compressed.pdf',
            'method': 'Text search (interim mode)',
            'status': 'PARTIAL'
        }

def main():
    """Interactive Q&A session."""
    print("=" * 60)
    print("🎓 OnDemand Tutor Q&A - INTERIM MODE")
    print("Working with your PDF while AI components install")
    print("=" * 60)
    print()
    
    qa = InterimQA()
    if not qa.pdf_text:
        print("Error: Could not load PDF. Please check the file exists.")
        return
    
    print("✓ Your PDF is loaded and ready!")
    print("✓ Ask questions about Network Security content")
    print("✓ Type 'quit' to exit")
    print()
    
    # Answer your previous question immediately
    previous_question = "what is network security"
    print(f">>> {previous_question}")
    result = qa.answer_question(previous_question)
    print(f"\n**Answer:**")
    print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
    print(f"\n**Source:** {result['source']}")
    print(f"**Method:** {result['method']}")
    print("\n" + "="*60 + "\n")
    
    # Interactive mode
    while True:
        try:
            question = input("Ask a question (or 'quit'): ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if not question:
                continue
            
            print(f"\nSearching PDF for: {question}")
            result = qa.answer_question(question)
            
            print(f"\n**Answer:**")
            # Limit output length for readability
            answer = result['answer']
            if len(answer) > 800:
                answer = answer[:800] + "...\n[Answer truncated - full AI system will provide complete responses]"
            print(answer)
            print(f"\n**Source:** {result['source']}")
            print(f"**Status:** {result['status']}")
            print("\n" + "-"*40 + "\n")
            
        except KeyboardInterrupt:
            break
    
    print("\nThank you for using the interim Q&A system!")
    print("The full AI system will be ready soon with:")
    print("• Semantic search and embeddings")
    print("• AI-generated contextual answers") 
    print("• Multiple source references")
    print("• Advanced question understanding")

if __name__ == "__main__":
    main()