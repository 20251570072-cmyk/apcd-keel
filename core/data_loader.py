"""
KEEL Data Loader
Reads all raw EXCEL/CSV files from the `data/raw/` subfolders and loads them into a single SQLite database at 
'data/processed/apcd_keel.db'. 
"""

import pandas as pd
import sqlite3
from pathlib import Path
import re

# Paths

DB_PATH = Path(__file__).parent.parent/"data"/"processed"/"apcd_keel.db"
RAW_PATH = Path(__file__).parent.parent/"data"/"raw"
MONTH_MAP = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}

def get_connection():
    """ 
    Open (or create) the SQLite database and return a connection object.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_schema():
    """
    Create all tables
    """
    conn = get_connection()
    conn.executescript("""
                       -- 1. aggregate trade volumes
                       CREATE TABLE IF NOT EXISTS trade_volumes (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           year INTEGER,
                           quarter INTEGER,
                           trade_type TEXT CHECK(trade_type IN ('import', 'export', 're-export')),
                           region_en TEXT,
                           region_ar TEXT,
                           value_aed REAL,
                           weight_ton REAL,
                           source_file TEXT
                        );
                        CREATE INDEX IF NOT EXISTS idx_trade_region ON trade_volumes(region_en);
                        CREATE INDEX IF NOT EXISTS idx_trade_year ON trade_volumes(year, quarter);

                        -- 2. Truck Turnaround Time
                        CREATE TABLE IF NOT EXISTS turnaround_times (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            year INTEGER,
                            quarter INTEGER,
                            ttt_hours REAL,
                            source_file TEXT
                        );

                         -- 3. Port capacity metrics (TEU = count, hence INTEGER)
                        CREATE TABLE IF NOT EXISTS port_capacity (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            year INTEGER,
                            quarter INTEGER,
                            gcr_rate REAL,
                            teu_count INTEGER,
                            vor_rate REAL,
                            source_file TEXT
                        );

                        -- 4. Violations & warnings
                        CREATE TABLE IF NOT EXISTS violations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            year INTEGER,
                            month_number INTEGER,
                            month_en TEXT,
                            month_ar TEXT,
                            service_en TEXT,
                            service_ar TEXT,
                            category_en TEXT,
                            category_ar TEXT,
                            violation_count INTEGER,
                            source_file TEXT
                        );

                        -- 5. Export certificates by goods
                         CREATE TABLE IF NOT EXISTS export_certificates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            certificate_number TEXT,
                            destination_en TEXT,
                            destination_ar TEXT,
                            invoice_value_aed REAL,
                            product_code TEXT,
                            product_desc_en TEXT,
                            product_desc_ar TEXT,
                            cert_year INTEGER,
                            transport_method TEXT,
                            transport_method_ar TEXT,
                            customer_id TEXT,
                            invoice_date TEXT,
                            final_destination_en TEXT,
                            final_destination_ar TEXT,
                            source_file TEXT
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_export_cert_customer ON export_certificates(customer_id);

                        -- 6. Export by product (HS-code level)
                        CREATE TABLE IF NOT EXISTS export_by_product (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            serial_number TEXT,
                            country_en TEXT,
                            country_ar TEXT,
                            amount_aed REAL,
                            cert_month INTEGER,
                            cert_date TEXT,
                            cert_year INTEGER,
                            hs_code TEXT,
                            hs_desc_en TEXT,
                            hs_desc_ar TEXT,
                            transport_ar TEXT,
                            transport_en TEXT,
                            coo_invoice TEXT,
                            invoice_date TEXT,
                            final_destination_en TEXT,
                            final_destination_ar TEXT,
                            source_file TEXT
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_export_product_hs ON export_by_product(hs_code);
                        CREATE INDEX IF NOT EXISTS idx_export_product_country ON export_by_product(country_en);

                        -- 7. Re-export certificates
                        CREATE TABLE IF NOT EXISTS reexport_certificates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            certificate_number TEXT,
                            customer_id TEXT,
                            customer_name TEXT,
                            final_destination TEXT,
                            certificate_date TEXT,
                            total_amount_aed REAL,
                            exporting_country_ar TEXT,
                            exporting_country_en TEXT,
                            invoice_value_aed REAL,
                            value_from_customer REAL,
                            source_file TEXT
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_reexport_customer ON reexport_certificates(customer_id);

                        -- 8. Economic permits (real company names)
                        CREATE TABLE IF NOT EXISTS economic_permits (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            permit_type_en TEXT,
                            permit_type_ar TEXT,
                            permit_start TEXT,
                            permit_end TEXT,
                            trade_name_en TEXT,
                            trade_name_ar TEXT,
                            license_source_en TEXT,
                            license_source_ar TEXT,
                            license_number TEXT,
                            source_file TEXT
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_permits_company ON economic_permits(trade_name_en);

                        -- 9. Health release certificates
                        CREATE TABLE IF NOT EXISTS health_certificates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            year INTEGER,
                            month_number INTEGER,
                            month_en TEXT,
                            month_ar TEXT,
                            service_en TEXT,
                            service_ar TEXT,
                            noc_count INTEGER,
                            source_file TEXT
                        );

                        -- 10. Waste stream
                        CREATE TABLE IF NOT EXISTS waste_stream (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            year INTEGER,
                            waste_type TEXT,
                            value_tonnes REAL,
                            source_file TEXT
                        );

                        -- 11. Company research (manual seed)
                        CREATE TABLE IF NOT EXISTS company_research (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            company_name TEXT,
                            industry TEXT,
                            hs_codes TEXT,
                            activity_type TEXT,
                            match_potential TEXT
                        );

                        -- 12. AI-generated country trust scores (populated by trust_model.py)
                        CREATE TABLE IF NOT EXISTS country_trust_scores (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            country_en TEXT,
                            year INTEGER,
                            quarter INTEGER,
                            trust_score REAL,
                            reliability_tier TEXT,
                            feature_consistency REAL,
                            feature_volume_stability REAL,
                            feature_regularity REAL,
                            feature_reexport_ratio REAL,
                            feature_avg_invoice_value REAL,
                            feature_hs_diversity REAL,
                            model_version TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_trust_country ON country_trust_scores(country_en);

                        -- 13. AI-generated product circular matches
                        CREATE TABLE IF NOT EXISTS product_circular_matches (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            hs_code_a TEXT,
                            product_a TEXT,
                            hs_code_b TEXT,
                            product_b TEXT,
                            match_score REAL,
                            match_logic TEXT,
                            model_version TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_match_hs_a ON product_circular_matches(hs_code_a);
                        CREATE INDEX IF NOT EXISTS idx_match_hs_b ON product_circular_matches(hs_code_b);
    """)
    
    conn.close()
    print("✅ Database schema initialized successfully.")
    
# Helper: clean column names
def clean_columns(df):
    """
    Clean column names by stripping whitespace, converting to lowercase, and replacing spaces with underscores.
    """
    new_cols = []
    for c in df.columns:
        c = str(c).lower().strip()
        c = c.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_").replace("-", "_")
        c = re.sub(r'_+', '_', c)
        new_cols.append(c)
    df.columns = new_cols
    return df

# Helper: safe read CSV/Excel
def safe_read_excel(path):
    """
    Read an Excel file safely, returning a DataFrame. If the file is not found or cannot be read, return None.
    """
    try:
        return pd.read_excel(path, engine='openpyxl')
    except Exception as e:
        print(f"⚠️ Error reading Excel file {path.name}: {e}")
        return None
    
# Helper: extract month number
def extract_month_number(df, month_col = "month_en"):
    """
    Extract month number from month name in the specified column.
    """
    if month_col in df.columns:
        df["month_number"] = df[month_col].astype(str).str.lower().str.strip().map(MONTH_MAP)
    return df

# Loaders for each dataset type
def load_trade_volume(file_path, trade_type):
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)
    
    rename = {
        'year': 'year',
        'qtr': 'quarter',
        'qr' : 'quarter',
        'region_en': 'region_en',
        'region_ar': 'region_ar',
        'value_aed': 'value_aed',
        'value_in_aed': 'value_aed',
        'weight_ton': 'weight_ton',
        'weight_tonnes':'weight_ton',
        'weight': 'weight_ton',
        'region': 'region_en',
        'country': 'region_en'         
    }
    
    df = df.rename(columns = {k: v for k, v in rename.items() if k in df.columns})
    
    for col in ['year', 'quarter', 'region_en', 'value_aed']:
        if col not in df.columns:
            print(f"⚠️ Missing required column '{col}' in {file_path.name}. Skipping this file.")
            print(f"Columns found: {list(df.columns)}")
            return 0
    
    df['trade_type'] = trade_type
    df['source_file'] = file_path.name
    
    conn = get_connection()
    df.to_sql('trade_volumes', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅ Loaded {len(df)} rows from {file_path.name} ({trade_type})")
    return len(df)

def load_ttt(file_path):  
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)
    
    rename = {
        'ttt': 'ttt_hours',
        'truck_turnaround_time': 'ttt_hours',
        'turnaround_time': 'ttt_hours',
        'value': 'ttt_hours',
        'ttt_in_minutes': 'ttt_hours',
        'qtr': 'quarter',
        'qr': 'quarter'
    }
    
    df= df.rename(columns = {k: v for k, v in rename.items() if k in df.columns})
    
    if 'ttt_hours'not in df.columns:
        print(f"⚠️ Missing required column 'ttt_hours' in {file_path.name}.")
        print(f"Columns found: {list(df.columns)}")
        return 0
    
    df['source_file'] = file_path.name
    conn = get_connection()
    df.to_sql('turnaround_times', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅ Loaded {len(df)} rows from {file_path.name} (Truck Turnaround Time)")   
    return len(df)

def load_port_metric(file_path, metric_name):
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    rename = {
        'value': metric_name,
        'rate': metric_name,
        'count': metric_name,
        'gcr': 'gcr_rate',
        'teu': 'teu_count',
        'teuin_ton': 'teu_count',
        'vor': 'vor_rate',
        'vor_in_hours': 'vor_rate',
        'qtr': 'quarter',
        'qr': 'quarter'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if metric_name not in df.columns:
        print(f"⚠️  Missing '{metric_name}' in {file_path.name}")
        print(f"   Found: {list(df.columns)}")
        return 0

    # Ensure all port_capacity columns exist
    for col in ['year', 'quarter', 'gcr_rate', 'teu_count', 'vor_rate']:
        if col not in df.columns:
            df[col] = None

    df = df[['year', 'quarter', 'gcr_rate', 'teu_count', 'vor_rate']]
    df['source_file'] = file_path.name

    conn = get_connection()
    df.to_sql('port_capacity', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} ({metric_name})")
    return len(df)




def load_violations(file_path):
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    rename = {
        'month_en': 'month_en',
        'month_ar': 'month_ar',
        'service_en': 'service_en',
        'service_ar': 'service_ar',
        'category_en': 'category_en',
        'category_ar': 'category_ar',
        'number_of_alarms_and_violations': 'violation_count',
        'number_of_alarms_violations': 'violation_count',
        'no_of_alarms_and_violations': 'violation_count',
        'number_of_alarms': 'violation_count'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if 'violation_count' not in df.columns:
        for c in df.columns:
            if 'number' in c and ('alarm' in c or 'violation' in c):
                df = df.rename(columns={c: 'violation_count'})
                break

    df = extract_month_number(df, 'month_en')
    df['source_file'] = file_path.name

    conn = get_connection()
    df.to_sql('violations', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (violations)")
    return len(df)


def load_export_by_goods(file_path):
    """Certificate-level export data."""
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    rename = {
        'certificate_number_issue_by_the_ajman_chamber': 'certificate_number',
        'certificate': 'certificate_number',
        'destination': 'destination_en',
        'destination_country_english': 'destination_en',
        'destination_country_arabic': 'destination_ar',
        'destination_ar': 'destination_ar',
        'aed_invoice': 'invoice_value_aed',
        'code_of_pr': 'product_code',
        'method_of': 'transport_method',
        'method_of_ar': 'transport_method_ar',
        'customer_i': 'customer_id',
        'final_desti': 'final_destination_en',
        'product_reached_as_per_invoice': 'product_desc_en',
        'product_description_english': 'product_desc_en',
        'product_description_arabic': 'product_desc_ar'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Safety net: only keep schema columns
    schema_cols = [
        'certificate_number', 'destination_en', 'destination_ar',
        'invoice_value_aed', 'product_code', 'product_desc_en',
        'product_desc_ar', 'cert_year', 'transport_method',
        'transport_method_ar', 'customer_id', 'invoice_date',
        'final_destination_en', 'final_destination_ar', 'source_file'
    ]
    df['source_file'] = file_path.name
    df = df[[c for c in df.columns if c in schema_cols]]

    conn = get_connection()
    df.to_sql('export_certificates', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (export certificates)")
    return len(df)


def load_export_by_product(file_path):
    """HS-code-level export data."""
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    rename = {
        'cooserialno': 'serial_number',
        'countryen': 'country_en',
        'countryar': 'country_ar',
        'aedamount': 'amount_aed',
        'certmonth': 'cert_month',
        'certdate': 'cert_date',
        'certyear': 'cert_year',
        'hscode': 'hs_code',
        'hsdescrip': 'hs_desc_en',
        'hsdescriptionen': 'hs_desc_en',
        'hsdescriptionar': 'hs_desc_ar',
        'hsdescripar': 'hs_desc_ar',
        'motar': 'transport_ar',
        'moten': 'transport_en',
        'cooinv': 'coo_invoice',
        'invoicedat': 'invoice_date',
        'finaldestin': 'final_destination_en',
        'finaldestinar': 'final_destination_ar'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    schema_cols = [
        'serial_number', 'country_en', 'country_ar', 'amount_aed',
        'cert_month', 'cert_date', 'cert_year', 'hs_code', 'hs_desc_en',
        'hs_desc_ar', 'transport_ar', 'transport_en', 'coo_invoice',
        'invoice_date', 'final_destination_en', 'final_destination_ar', 'source_file'
    ]
    df['source_file'] = file_path.name
    df = df[[c for c in df.columns if c in schema_cols]]

    conn = get_connection()
    df.to_sql('export_by_product', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (export by product)")
    return len(df)


def load_reexport(file_path):
    """Re-export certificate data."""
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    # Expanded rename to handle every typo variant found in APCD files
    rename = {
        'certificate_number_issue_by_the_ajman_chamber': 'certificate_number',
        'certificate': 'certificate_number',
        'customer_i': 'customer_id',
        'cutomer_i': 'customer_id',
        'customer_invoice_number': 'customer_id',
        'cutomer_invoice_number': 'customer_id',
        'final_desti': 'final_destination',
        'total_amou': 'total_amount_aed',
        'exporting_c': 'exporting_country_ar',
        'exporting_c_en': 'exporting_country_en',
        'aed_invoice': 'invoice_value_aed',
        'value_from_customer': 'value_from_customer',
        'invoice_date': 'certificate_date',
        'cutomer_invoice_date': 'certificate_date',
        'cert_date': 'certificate_date'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Safety net: only keep columns that actually exist in our schema
    schema_cols = [
        'certificate_number', 'customer_id', 'customer_name',
        'final_destination', 'certificate_date', 'total_amount_aed',
        'exporting_country_ar', 'exporting_country_en',
        'invoice_value_aed', 'value_from_customer', 'source_file'
    ]
    # Add source_file
    df['source_file'] = file_path.name
    
    # Drop any columns not in schema (prevents future typos from crashing)
    df = df[[c for c in df.columns if c in schema_cols]]

    conn = get_connection()
    df.to_sql('reexport_certificates', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (re-export)")
    return len(df)


def load_economic_permits(file_path):
    """ Real company names and permit data."""
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    # Handle both snake_case and camelCase column names
    rename = {
        'permittyp': 'permit_type_en',
        'permittype': 'permit_type_en',
        'permittypeen': 'permit_type_en',
        'permittypear': 'permit_type_ar',
        'permitstar': 'permit_start',
        'permitstart': 'permit_start',
        'permitend': 'permit_end',
        'tradenam': 'trade_name_en',
        'tradenamen': 'trade_name_en',
        'tradenameen': 'trade_name_en',
        'tradenamear': 'trade_name_ar',
        'licenseso': 'license_source_en',
        'licensesourceen': 'license_source_en',
        'licensesourcear': 'license_source_ar',
        'licensenumber': 'license_number'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Safety net: only keep schema columns
    schema_cols = [
        'permit_type_en', 'permit_type_ar', 'permit_start', 'permit_end',
        'trade_name_en', 'trade_name_ar', 'license_source_en',
        'license_source_ar', 'license_number', 'source_file'
    ]
    df['source_file'] = file_path.name
    df = df[[c for c in df.columns if c in schema_cols]]

    conn = get_connection()
    df.to_sql('economic_permits', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (economic permits)")
    return len(df)


def load_health_certificates(file_path):
    """
    Health release certificates
    """
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    rename = {
        'month_en': 'month_en',
        'month_ar': 'month_ar',
        'service_en': 'service_en',
        'service_ar': 'service_ar',
        'number_of_noc': 'noc_count',
        'no_of_noc': 'noc_count',
        'noc': 'noc_count'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if 'noc_count' not in df.columns:
        for c in df.columns:
            if 'number' in c or 'noc' in c:
                df = df.rename(columns={c: 'noc_count'})
                break

    df = extract_month_number(df, 'month_en')
    df['source_file'] = file_path.name

    conn = get_connection()
    df.to_sql('health_certificates', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (health certs)")
    return len(df)


def load_waste_stream(file_path):
    """ Waste data."""
    df = safe_read_excel(file_path)
    if df is None:
        return 0
    df = clean_columns(df)

    rename = {
        'waste_stre': 'waste_type',
        'waste_stream': 'waste_type',
        'waste_stream_in_tonnes': 'waste_type',
        'value': 'value_tonnes',
        'tonnes': 'value_tonnes',
        'waste_value': 'value_tonnes'
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    schema_cols = ['year', 'waste_type', 'value_tonnes', 'source_file']
    df['source_file'] = file_path.name
    df = df[[c for c in df.columns if c in schema_cols]]

    conn = get_connection()
    df.to_sql('waste_stream', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: {file_path.name} (waste)")
    return len(df)


def load_company_research(file_path):
    """
    The manual CSV
    """
    if not file_path.exists():
        return 0
    df = pd.read_csv(file_path)
    df = clean_columns(df)

    conn = get_connection()
    df.to_sql('company_research', conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅  Loaded {len(df)} rows: company_research.csv")
    return len(df)


# Main orchestrator
def build_database():
    print("=" * 60)
    print("🏗️  KEEL DATABASE BUILDER")
    print("=" * 60)

    init_schema()

    total_rows = 0

    # Walk all subfolders in data/raw 
    for folder in RAW_PATH.iterdir():
        if not folder.is_dir():
            continue

        print(f"\n📂 Scanning folder: {folder.name}")

        for file in folder.iterdir():
            if not file.is_file():
                continue
            fname = file.name.lower()

            if not fname.endswith(('.xlsx', '.xls', '.csv')):
                continue

            # ── TIER 1 / AGGREGATE: Trade volumes ─────────────────
            if re.search(r'import.*region.*\.xlsx?$', fname):
                total_rows += load_trade_volume(file, 'import')
            elif re.search(r'export.*region.*\.xlsx?$', fname):
                total_rows += load_trade_volume(file, 'export')
            elif re.search(r're[-_]?export.*region.*\.xlsx?$', fname):
                total_rows += load_trade_volume(file, 're-export')

            # ── TIER 1 / AGGREGATE: TTT ───────────────────────────
            elif re.search(r'ttt.*\.xlsx?$', fname):
                total_rows += load_ttt(file)

            # ── TIER 1 / AGGREGATE: Port metrics ──────────────────
            elif re.search(r'gcr.*\.xlsx?$', fname):
                total_rows += load_port_metric(file, 'gcr_rate')
            elif re.search(r'teu.*\.xlsx?$', fname):
                total_rows += load_port_metric(file, 'teu_count')
            elif re.search(r'vor.*\.xlsx?$', fname):
                total_rows += load_port_metric(file, 'vor_rate')

            # ── TIER 2: Chamber / Economic data ───────────────────
            elif re.search(r'export.*goods.*\.xlsx?$', fname):
                total_rows += load_export_by_goods(file)
            elif re.search(r'export.*product.*\.xlsx?$', fname):
                total_rows += load_export_by_product(file)
            elif re.search(r're[-_]?export.*country.*\.xlsx?$', fname):
                total_rows += load_reexport(file)
            elif re.search(r'economic.*permit.*\.xlsx?$', fname):
                total_rows += load_economic_permits(file)

            # ── TIER 2 / TIER 3: Municipal ──────────────────────
            elif re.search(r'warning.*violation.*\.xlsx?$', fname):
                total_rows += load_violations(file)
            elif re.search(r'health.*release.*\.xlsx?$', fname):
                total_rows += load_health_certificates(file)
            elif re.search(r'waste.*stream.*\.xlsx?$', fname):
                total_rows += load_waste_stream(file)

            # ── Skip marine fees ──────────────────────────────────
            elif re.search(r'marine.*fee.*\.xlsx?$', fname):
                print(f"⏭️  Skipping {file.name} (marine fees — not needed for core)")


    # ── Load manual company research CSV ──────────────────────────
    for folder_name in ['tier2', 'Tier 2']:
        research_file = RAW_PATH / folder_name / 'company_research.csv'
        if research_file.exists():
            total_rows += load_company_research(research_file)
            break

    print("\n" + "=" * 60)
    print(f"🏁 DONE — Total rows loaded: {total_rows}")
    print(f"📁 Database: {DB_PATH}")
    print("=" * 60)


# Entry point
if __name__ == "__main__":
    build_database()
