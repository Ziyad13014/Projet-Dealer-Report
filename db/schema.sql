-- Database schema for dealer-report application
-- MySQL/MariaDB compatible

-- Rules per retailer
CREATE TABLE IF NOT EXISTS retailer_rules (
  retailer           VARCHAR(128) PRIMARY KEY,
  min_success_rate   FLOAT NULL,   -- e.g. 0.95 for 95%
  min_progress_0930  FLOAT NULL,   -- e.g. 0.10 for 10%
  include_successes  TINYINT(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- One row per crawler execution
CREATE TABLE IF NOT EXISTS crawler_runs (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  retailer     VARCHAR(128) NOT NULL,
  planned_for  DATE NOT NULL,       -- the day this run belongs to
  started_at   DATETIME NOT NULL,
  finished_at  DATETIME NULL,
  status       ENUM('success','error','running','queued') NOT NULL,
  total_items  INT NULL,
  ok_items     INT NULL,
  ko_items     INT NULL,
  KEY idx_runs_by_retailer_date (retailer, planned_for),
  KEY idx_runs_started (planned_for, started_at),
  KEY idx_runs_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional planning table (if you know the expected total per day per retailer)
CREATE TABLE IF NOT EXISTS runs_plan (
  plan_date      DATE NOT NULL,
  retailer       VARCHAR(128) NOT NULL,
  expected_total INT NOT NULL,
  PRIMARY KEY (plan_date, retailer)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
