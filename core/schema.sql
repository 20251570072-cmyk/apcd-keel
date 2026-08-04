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
CREATE TABLE reexport_certificated (
  
);
