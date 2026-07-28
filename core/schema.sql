-- Database Schema of KEEL (full APCD + AFZ + Municipal Data)

-- 1| (export/import/re-export) volumes by region
CREATE TABLE trade_volumes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  yesr INTEGER,
  quarter INTEGER,
  region_en TEXT,
  region_ar TEXT,
  value_aed REAL,
  weight_ton TEXT CHECK(trade_type IN ('import', 'export', 're-export')),
  source_file TEXT,
  UNIQUE(year, quarter, region_en, trade_type)
);
