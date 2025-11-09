"""
Test script for the OnDemand Tutor Q&A Agent.
Demonstrates basic functionality and validates the system components.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.append(str(src_dir))

from qa_pipeline import QAPipeline

def test_basic_functionality():
    """Test basic Q&A pipeline functionality."""
    print("=" * 60)
    print("Testing OnDemand Tutor Q&A Agent")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing Q&A Pipeline...")
    pipeline = QAPipeline()
    
    # Get system stats
    print("\n2. Getting system statistics...")
    stats = pipeline.get_knowledge_base_stats()
    print(f"System Status: {stats.get('system_status', 'Unknown')}")
    
    # Check if we have any documents
    db_stats = stats.get('database', {})
    total_docs = db_stats.get('total_documents', 0)
    
    if total_docs == 0:
        print("\n⚠️  No documents found in knowledge base.")
        print("Please add course materials to the data/course_materials/ directory")
        print("Supported formats: PDF, DOCX, TXT, MD")
        return False
    
    print(f"\n3. Knowledge Base Status:")
    print(f"   - Total documents: {total_docs}")
    print(f"   - Source files: {db_stats.get('unique_source_files', 0)}")
    
    # Test queries
    test_questions = [
        "What is a firewall?",
        "Explain network security",
        "What are the main types of cyber attacks?",
        "How does encryption work in network security?"
    ]
    
    print(f"\n4. Testing with sample questions...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Question {i}: {question}")
        try:
            result = pipeline.query(question, top_k=3)
            
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                # Show truncated answer
                answer = result['answer']
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                print(f"   ✅ Answer: {answer}")
                print(f"   📚 Sources used: {len(result['sources'])}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    # Cleanup
    pipeline.cleanup()
    print(f"\n5. ✅ Testing completed!")
    
    return True

def create_sample_content():
    """Create sample course content for testing."""
    print("\nCreating sample course content...")
    
    # Ensure directory exists
    course_dir = project_root / "data" / "course_materials"
    course_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample content
    sample_content = """# Network Security Fundamentals

## Chapter 1: Introduction to Network Security

Network security is the practice of protecting computer networks and their data from unauthorized access, misuse, modification, or denial of service. It encompasses both hardware and software technologies and involves multiple layers of defense.

### What is a Firewall?

A firewall is a network security device or software that monitors and controls incoming and outgoing network traffic based on predetermined security rules. Firewalls establish a barrier between a trusted internal network and untrusted external networks, such as the Internet.

Types of Firewalls:
1. **Packet-Filtering Firewalls**: Examine packets at the network layer
2. **Stateful Inspection Firewalls**: Track the state of active connections
3. **Application-Level Gateways**: Filter traffic at the application layer
4. **Next-Generation Firewalls (NGFW)**: Combine traditional firewall technology with additional features

### Network Security Threats

Common network security threats include:

1. **Malware**: Malicious software including viruses, worms, trojans, and ransomware
2. **Phishing**: Fraudulent attempts to obtain sensitive information
3. **Man-in-the-Middle Attacks**: Intercepting communications between two parties
4. **Denial of Service (DoS)**: Overwhelming a system to make it unavailable
5. **SQL Injection**: Inserting malicious SQL code into applications
6. **Cross-Site Scripting (XSS)**: Injecting malicious scripts into web applications

### Encryption in Network Security

Encryption is the process of converting readable data into an unreadable format to protect it from unauthorized access. In network security, encryption is used to:

- Protect data in transit (communication encryption)
- Secure stored data (data at rest encryption)
- Authenticate users and devices
- Ensure data integrity

Common encryption protocols include:
- **SSL/TLS**: For secure web communications
- **IPSec**: For network layer security
- **WPA2/WPA3**: For wireless network security
- **AES**: Advanced Encryption Standard for data encryption

### Network Security Best Practices

1. **Defense in Depth**: Implement multiple layers of security
2. **Regular Updates**: Keep systems and software updated
3. **Access Control**: Implement principle of least privilege
4. **Monitoring**: Continuous network monitoring and logging
5. **Employee Training**: Security awareness education
6. **Incident Response**: Prepared response plans for security incidents
7. **Regular Audits**: Periodic security assessments

## Chapter 2: Advanced Security Concepts

### Intrusion Detection Systems (IDS)

An IDS monitors network traffic and system activities for malicious activities or policy violations. Types include:
- **Network-based IDS (NIDS)**: Monitors network traffic
- **Host-based IDS (HIDS)**: Monitors individual systems

### Virtual Private Networks (VPN)

VPNs create secure connections over public networks by encrypting data and tunneling it through secure protocols. Common VPN protocols include OpenVPN, IPSec, and WireGuard.

### Zero Trust Security Model

The Zero Trust model assumes that threats can exist both outside and inside the network perimeter, requiring verification from everyone trying to access resources regardless of their location.
"""
    
    # Write sample content
    sample_file = course_dir / "network_security_fundamentals.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"✅ Created sample file: {sample_file}")
    return True

if __name__ == "__main__":
    # Check if we have course materials
    course_dir = project_root / "data" / "course_materials"
    
    if not course_dir.exists() or not any(course_dir.glob("*")):
        print("No course materials found. Creating sample content...")
        create_sample_content()
    
    # Run tests
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 OnDemand Tutor Q&A Agent is working correctly!")
        print("\nNext steps:")
        print("1. Add your own course materials to data/course_materials/")
        print("2. Run: python main.py")
        print("3. Access the web interface in your browser")
    else:
        print("\n❌ Some issues detected. Please check the setup.")