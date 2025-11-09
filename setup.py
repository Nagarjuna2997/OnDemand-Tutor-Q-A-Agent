"""
Setup script for the OnDemand Tutor Q&A Agent.
Automates the initial setup and dependency installation.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Command succeeded: {command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    
    # Try to install packages one by one to handle potential issues
    packages = [
        "numpy",
        "pandas", 
        "python-dotenv",
        "streamlit",
        "PyPDF2",
        "python-docx",
        "gpt4all",
        "sentence-transformers",
        "chromadb"
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"Installing {package}...")
        success, output = run_command(f"pip install {package}")
        if not success:
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Failed to install: {', '.join(failed_packages)}")
        print("You may need to install these manually.")
        return False
    else:
        print("\n✅ All dependencies installed successfully!")
        return True

def create_directories():
    """Create necessary project directories."""
    print("\n📁 Creating project directories...")
    
    directories = [
        "data/course_materials",
        "data/processed",
        "models",
        "tests"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")

def create_sample_content():
    """Create sample course content if none exists."""
    course_dir = Path("data/course_materials")
    
    if not any(course_dir.glob("*")):
        print("\n📝 Creating sample course content...")
        
        sample_content = """# Network Security Quick Reference

## Firewalls
A firewall is a network security device that monitors and controls network traffic based on security rules.

## Encryption
Encryption converts readable data into unreadable format to protect against unauthorized access.

## Common Threats
- Malware
- Phishing
- Man-in-the-middle attacks
- Denial of Service (DoS)

## Best Practices
1. Use strong passwords
2. Keep software updated
3. Implement multi-factor authentication
4. Regular security audits
"""
        
        sample_file = course_dir / "sample_network_security.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"✅ Created sample file: {sample_file}")

def main():
    """Main setup function."""
    print("🎓 OnDemand Tutor Q&A Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("\nPlease upgrade to Python 3.8 or later and try again.")
        return False
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup completed with warnings. You may need to install some packages manually.")
    
    # Create sample content
    create_sample_content()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Add your course materials (PDF, DOCX, TXT, MD) to data/course_materials/")
    print("2. Run: python main.py")
    print("3. Access the web interface at the URL shown")
    print("\nFor testing, you can also run: python tests/test_pipeline.py")
    
    return True

if __name__ == "__main__":
    main()