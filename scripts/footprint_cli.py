#!/usr/bin/env python3
"""
Footprint Scanner CLI
Command-line interface for analyzing digital footprint.

Usage:
    footprint-scan --github username --linkedin url --so user_id --out ./reports
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.footprint_scanner import FootprintScanner


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze professional digital footprint across platforms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  footprint-scan --github torvalds --out ./reports
  footprint-scan --github octocat --so 12345 --linkedin https://linkedin.com/in/user
  footprint-scan --github myuser --enable-scraping --linkedin-consent
        """
    )
    
    # Platform arguments
    parser.add_argument('--github', dest='github_username', help='GitHub username')
    parser.add_argument('--linkedin', dest='linkedin_url', help='LinkedIn profile URL')
    parser.add_argument('--so', '--stackoverflow', dest='stackoverflow_id', help='StackOverflow user ID')
    
    # Output arguments
    parser.add_argument('--out', '--output', dest='output_dir', default='./reports',
                        help='Output directory for reports (default: ./reports)')
    parser.add_argument('--format', choices=['text', 'json', 'both'], default='both',
                        help='Report format (default: both)')
    
    # API credentials
    parser.add_argument('--github-token', dest='github_token',
                        default=os.getenv('GITHUB_TOKEN'),
                        help='GitHub Personal Access Token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--so-key', dest='so_key',
                        default=os.getenv('STACKOVERFLOW_KEY'),
                        help='StackOverflow API key (or set STACKOVERFLOW_KEY env var)')
    
    # LinkedIn scraping options
    parser.add_argument('--enable-scraping', action='store_true',
                        help='Enable LinkedIn scraping (disabled by default)')
    parser.add_argument('--linkedin-consent', action='store_true',
                        help='Confirm user consent for LinkedIn scraping')
    
    # Other options
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate inputs
    if not any([args.github_username, args.linkedin_url, args.stackoverflow_id]):
        parser.error('At least one platform must be specified (--github, --linkedin, or --so)')
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize scanner
    logger.info("Initializing Footprint Scanner...")
    scanner = FootprintScanner(
        github_token=args.github_token,
        stackoverflow_key=args.so_key,
        enable_linkedin_scraping=args.enable_scraping
    )
    
    # Determine output files
    timestamp = Path(output_dir) / f"footprint_{Path(args.github_username or args.stackoverflow_id or 'report').stem}"
    text_output = f"{timestamp}.txt" if args.format in ['text', 'both'] else None
    json_output = f"{timestamp}.json" if args.format in ['json', 'both'] else None
    
    # Run analysis
    logger.info("Starting footprint analysis...")
    print("\n" + "="*60)
    print("DIGITAL FOOTPRINT ANALYSIS")
    print("="*60)
    
    if args.github_username:
        print(f"• GitHub: {args.github_username}")
    if args.linkedin_url:
        print(f"• LinkedIn: {args.linkedin_url}")
    if args.stackoverflow_id:
        print(f"• StackOverflow: {args.stackoverflow_id}")
    
    print("="*60 + "\n")
    
    try:
        analysis = scanner.analyze_footprint(
            github_username=args.github_username,
            linkedin_url=args.linkedin_url,
            stackoverflow_user_id=args.stackoverflow_id,
            linkedin_consent=args.linkedin_consent,
            export_text=text_output,
            export_json=json_output
        )
        
        if not analysis.get("success"):
            logger.error("Analysis failed")
            print("\n❌ Analysis failed. Check logs for details.")
            return 1
        
        # Print summary
        summary = scanner.get_summary(analysis)
        
        print(f"\n📊 RESULTS SUMMARY")
        print("-" * 60)
        print(f"Overall Score: {summary['overall_score']}/100 ({summary['overall_rating']})")
        print(f"Platforms Analyzed: {', '.join(summary['platforms_analyzed'])}")
        print()
        
        if summary.get('platform_scores'):
            print("Platform Scores:")
            for platform, score in summary['platform_scores'].items():
                if score > 0:
                    print(f"  • {platform.capitalize()}: {score}/100")
        print()
        
        if summary.get('top_strengths'):
            print("✓ Top Strengths:")
            for strength in summary['top_strengths']:
                print(f"  • {strength}")
            print()
        
        if summary.get('top_recommendations'):
            print("💡 Top Recommendations:")
            for i, rec in enumerate(summary['top_recommendations'], 1):
                print(f"  {i}. {rec}")
            print()
        
        # Report file locations
        print("="*60)
        print("📁 REPORTS GENERATED")
        print("="*60)
        if text_output:
            print(f"  Text: {text_output}")
        if json_output:
            print(f"  JSON: {json_output}")
        print()
        
        logger.info("Analysis completed successfully")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis cancelled by user")
        return 130
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
