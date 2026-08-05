-- Database Schema of KEEL (full APCD + AFZ + Municipal Data)

-- 1| (export/import/re-export) volumes by region
CREATE TABLE trade_volumes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTEGER,
  quarter INTEGER,
  region_en TEXT,
  region_ar TEXT,
  value_aed REAL,
  weight_ton TEXT CHECK(trade_type IN ('import', 'export', 're-export')),
  source_file TEXT,
  UNIQUE(year, quarter, region_en, trade_type)
);

-- 2| Truck Turnaround Times
CREATE TABLE turnaround_times (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTIGER,
  quarter INTEGER,
  ttt_hours REAL,
  source_file TEXT,
  UNIQUE(year, quarter)
);

-- 3| (GCR + TEU + VOR) Port Capacity Metrics
CREATE TABLE port_capacity(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTEGER,
  quarter INTEGER,
  gcr_rate REAL,
  teu_count REAL,
  vor_rate REAL,
  source_file TEXT,
  UNIQUE(year, quarter)
);

-- 4| Violations & Warnings (reputation proxy)
CREATE TABLE violations(
  id PRIMARY KEY AUTOINCREMENT,
  year INTEGER,
  month_en TEXT,
  month_ar TEXT,
  service_en TEXT,
  service_ar TEXT,
  violation_count INTEGER,
  source_file TEXT
);

-- 5| Exports Certificates by Goods
CREATE TABLE export_certificates(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  certificate_no TEXT,
  destination_en TEXT,
  destination_ar TEXT,
  invoice_value_aed REAL,
  product_code TEXT,
  product_desc_en TEXT,
  product_desc_ar TEXT,
  year INTEGER,
  transport_method TEXT
  transport_method_ar TEXT,
  customer_id TEXT,
  invoice_date TEXT,
  final_destination TEXT,
  source_file TEXT
);

-- 6| Export Certificates by Product
CREATE TABLE export_by_product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  serial_no TEXT,
  country_en TEXT,
  amount_aed REAL,
  cert_month INTEGER,
  cert_date INTEGER,
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

--7| Re-export certifcates
CREATE TABLE reexport_certificates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  certificate_no TEXT,
  customer_id TEXT,
  customer_name TEXT,
  final_destination TEXT,
  cert_date TEXT,
  total_amount_aed REAL,
  exporting_country_ar TEXT,
  invoice_value_aed REAL,
  value_from_customer REAL,
  source_file TEXT
);

--8| Economic permits
CREATE TABLE economic_permit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  permit_type_en TEXT,
  permit_type_ar TEXT,
  permit_start DATE,
  permit_end DATE,
  trade_name_en TEXT,
  trade_name_ar TEXT,
  license_source_en TEXT,
  license_source_ar TEXT,
  license_number TEXT,
  source_file TEXT
);

--9| Company research 
CREATE TABLE company_research (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_name TEXT,
  industry TEXT,
  hs_codes TEXT,
  activity_type TEXT,
  match_potential TEXT
);

--10| AI generated country trust scores
CREATE TABLE country_trust_scores(
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
  created_at DATE DEFAULT CURRENT_DATE,
  UNIQUE(country_en, year, quarter)
);

--11| AI generated product circular matches
CREATE TABLE product_circular_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_code_a TEXT,
    product_a TEXT,
    hs_code_b TEXT,
    product_b TEXT,
    match_score REAL,
    match_logic TEXT,
    created_at DATE DEFAULT CURRENT_DATE
);
