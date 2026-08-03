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

-- 2| Truct Turnaround Times
CREATE TABLE turnaround_times (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTIGER,
  quarter INTEGER,
  ttt_hours REAL,
  source_file TEXT,
  UNIQUE(year, quarter)
);

--3| (GCR + TEU + VOR) Port Capacity Metrics
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
