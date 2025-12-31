from src.manager import ETLManager
from config import category_config_parser

if __name__ == "__main__":
    # Categories to skip or run specifically (can be adjusted)
    # running all configured categories
    
    categories = [cat for cat in category_config_parser.sections()]
    print(f"Starting ETL for {len(categories)} categories: {categories}")

    for category in categories:
        print(f"\n--- Processing Category: {category} ---")
        etl_process = ETLManager(category=category)
        # We will update run_etl to accept output_file
        etl_process.run_etl(output_file=f"outputs/output_{category}.xlsx", total_products=20) 
        # Reduced product count to 20 per category for faster processing

