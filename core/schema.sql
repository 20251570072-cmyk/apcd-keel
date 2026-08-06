-- Database Schema of KEEL (full APCD + AFZ + Municipal Data)

-- 1. Aggregate trade volumes
CREATE TABLE IF NOT EXISTS trade_volumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    quarter INTEGER,
    trade_type TEXT CHECK(trade_type IN ('import', 'export', 're-export')),
    region_en TEXT,
    region_ar TEXT,
    value_aed REAL,
    weight_ton REAL,
    source_file TEXT,
);

CREATE INDEX IF NOT EXISTS idx_trade_region ON trade_volumes(region_en);
CREATE INDEX IF NOT EXISTS idx_trade_year ON trade_volumes(year, quarter);

-- 2. Truck Turnaround Time
CREATE TABLE IF NOT EXISTS turnaround_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    quarter INTEGER,
    ttt_hours REAL,
    source_file TEXT,
);

-- 3. Port capacity metrics
-- TEU = Twenty-foot Equivalent Unit (a count), hence INTEGER
CREATE TABLE IF NOT EXISTS port_capacity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    quarter INTEGER,
    gcr_rate REAL,
    teu_count INTEGER,
    vor_rate REAL,
    source_file TEXT,
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

-- 11. Company research (manual seed — denormalized by design)
CREATE TABLE IF NOT EXISTS company_research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    industry TEXT,
    hs_codes TEXT,
    activity_type TEXT,
    match_potential TEXT
);

-- 12. AI-generated country trust scores
-- All features persisted for full explainability and retraining
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_en, year, quarter)
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
