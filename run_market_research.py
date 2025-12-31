
import os
import glob
from src.analysis.gemini_analyzer import GeminiAnalyzer

def get_available_outputs():
    # Only list files that match the pattern output_CATEGORY.xlsx in outputs/ directory
    files = glob.glob("outputs/output_*.xlsx")
    return sorted(files)

def main():
    print("Welcome to the Cosmetic Market Research Tool (Powered by Gemini Flash)")
    print("---------------------------------------------------------------------")

    # Check for API Key
    from decouple import config
    try:
        api_key = config("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("\n[ERROR] GEMINI_API_KEY is missing or invalid in .env file.")
            print("Please add your API Key to proceed.")
            return
    except:
         print("\n[ERROR] Could not read .env file.")
         return

    analyzer = GeminiAnalyzer()
    
    files = get_available_outputs()
    if not files:
        print("\nNo output files found in 'outputs/' directory. Please run the scraper first.")
        return

    print(f"\nFound {len(files)} category files:")
    for idx, f in enumerate(files):
        print(f"{idx + 1}. {f}")

    print("\nOr type 'ALL' to analyze all categories.")
    
    choice = input("\nEnter number of file to analyze (or 'ALL'): ").strip()
    
    selected_files = []
    if choice.upper() == 'ALL':
        selected_files = files
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            selected_files = [files[idx]]
        else:
            print("Invalid selection.")
            return
    else:
        print("Invalid input.")
        return

    for file_path in selected_files:
        print(f"\nAnalyzing {file_path}...")
        report = analyzer.analyze_category(file_path)
        
        print("\n" + "="*40)
        print(f"REPORT FOR {file_path}")
        print("="*40)
        print(report)
        print("="*40 + "\n")
        
        # Save report
        report_filename = file_path.replace(".xlsx", "_report.md")
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {report_filename}")

if __name__ == "__main__":
    main()
