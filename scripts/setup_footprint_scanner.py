#!/usr/bin/env python3
"""
Setup script for Footprint Scanner
Installs dependencies and verifies installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          FOOTPRINT SCANNER - SETUP & INSTALLATION             ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 11):
        print("⚠️  Warning: Python 3.11+ recommended")
    
    # Install Python dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        print("\n❌ Failed to install dependencies. Exiting.")
        return 1
    
    # Install Playwright browsers
    if not run_command(
        "playwright install chromium",
        "Installing Playwright browsers (for LinkedIn scraping)"
    ):
        print("\n⚠️  Playwright installation failed. LinkedIn scraping will not work.")
    
    # Create necessary directories
    print(f"\n{'='*60}")
    print("📁 Creating directories")
    print(f"{'='*60}")
    
    dirs = [
        "reports",
        "logs",
        "temp",
        "examples"
    ]
    
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"  ✅ {dir_name}/")
    
    # Setup .env file
    print(f"\n{'='*60}")
    print("⚙️  Environment Configuration")
    print(f"{'='*60}")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists() and env_example_path.exists():
        import shutil
        shutil.copy(env_example_path, env_path)
        print(f"  ✅ Created .env from .env.example")
        print(f"  ⚠️  Please edit .env and add your API credentials")
    elif env_path.exists():
        print(f"  ℹ️  .env already exists")
    
    # Verify installations
    print(f"\n{'='*60}")
    print("🔍 Verifying Installation")
    print(f"{'='*60}")
    
    verifications = []
    
    # Test imports
    try:
        from src.core.footprint_scanner import FootprintScanner
        print("  ✅ FootprintScanner module")
        verifications.append(True)
    except ImportError as e:
        print(f"  ❌ FootprintScanner module: {e}")
        verifications.append(False)
    
    try:
        from src.core.collectors.github_collector import GitHubCollector
        print("  ✅ GitHub collector")
        verifications.append(True)
    except ImportError as e:
        print(f"  ❌ GitHub collector: {e}")
        verifications.append(False)
    
    try:
        from src.core.collectors.stackoverflow_collector import StackOverflowCollector
        print("  ✅ StackOverflow collector")
        verifications.append(True)
    except ImportError as e:
        print(f"  ❌ StackOverflow collector: {e}")
        verifications.append(False)
    
    try:
        from src.core.collectors.linkedin_scraper import LinkedInScraper
        print("  ✅ LinkedIn scraper")
        verifications.append(True)
    except ImportError as e:
        print(f"  ❌ LinkedIn scraper: {e}")
        verifications.append(False)
    
    try:
        import playwright
        print("  ✅ Playwright installed")
        verifications.append(True)
    except ImportError:
        print("  ⚠️  Playwright not found (LinkedIn scraping unavailable)")
        verifications.append(False)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 INSTALLATION SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(verifications)
    total_count = len(verifications)
    
    print(f"Successful: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n✅ Installation complete! All components verified.")
    elif success_count >= 4:
        print("\n⚠️  Installation mostly complete. Some optional components missing.")
    else:
        print("\n❌ Installation incomplete. Please check errors above.")
        return 1
    
    # Print next steps
    print(f"\n{'='*60}")
    print("🎯 NEXT STEPS")
    print(f"{'='*60}")
    print("""
1. Edit .env file and add your API credentials:
   - GITHUB_TOKEN (get from: https://github.com/settings/tokens)
   - STACKOVERFLOW_KEY (get from: https://stackapps.com)

2. Test the installation:
   python scripts/footprint_cli.py --github torvalds --out ./reports

3. Read the documentation:
   docs/FOOTPRINT_SCANNER.md
   docs/FOOTPRINT_SCANNER_QUICKSTART.md

4. Run tests:
   pytest tests/test_footprint_scanner.py -v

Happy scanning! 🚀
    """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
