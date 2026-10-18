from pathlib import Path

# so I don't keep typing the same paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = ROOT / "reports"
STATIC_DIR = Path(__file__).resolve().parent / "static"

RAW_PRODUCTS = RAW_DIR / "open_beauty_facts_products.json"
DB_PATH = PROCESSED_DIR / "skinsync.sqlite"
RESULTS_JSON = RESULTS_DIR / "checkpoint1_results.json"
CP2_RESULTS_JSON = RESULTS_DIR / "checkpoint2_results.json"
