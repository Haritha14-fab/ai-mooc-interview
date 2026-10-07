"""Quick start script to initialize the application"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and return success status"""
    try:
        subprocess.run(cmd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("\n" + "="*50)
    print("AI MOOC Interview & Assessment System")
    print("Quick Start Script")
    print("="*50 + "\n")
    
    project_dir = Path(__file__).resolve().parent
    os.chdir(project_dir / 'backend')
    
    print("Creating demo data...")
    if run_command([sys.executable, 'seed.py']):
        print("✅ Demo data created successfully\n")
    else:
        print("⚠️  Could not create demo data (it may already exist)\n")
    
    os.chdir(project_dir)
    
    print("\n" + "="*50)
    print("Quick Start Complete!")
    print("="*50 + "\n")
    
    print("To start the application:\n")
    print("Terminal 1 - Start Backend:")
    print("  cd backend")
    print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("  python -m uvicorn app.main:app --reload\n")
    
    print("Terminal 2 - Start Frontend:")
    print("  cd frontend")
    print("  npm run dev\n")
    
    print("Then open: http://localhost:3000\n")
    
    print("Demo Login Credentials:")
    print("  Email: demo@example.com")
    print("  Password: demo1234\n")

if __name__ == "__main__":
    main()
