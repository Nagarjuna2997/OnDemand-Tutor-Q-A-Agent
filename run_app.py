#!/usr/bin/env python3
"""
Simple runner for OnDemand Tutor Q&A Agent without Unicode issues.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main entry point for the OnDemand Tutor Q&A Agent."""
    print("Starting OnDemand Tutor Q&A Agent...")
    print("Opening web interface...")
    
    # Get the path to the Streamlit app
    app_path = Path(__file__).parent / "src" / "ui" / "streamlit_app.py"
    
    # Run Streamlit with no email prompt
    try:
        env = os.environ.copy()
        env['STREAMLIT_CLIENT_SKIP_EMAIL'] = '1'
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ], env=env)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        print("You can manually run: streamlit run src/ui/streamlit_app.py")

if __name__ == "__main__":
    main()