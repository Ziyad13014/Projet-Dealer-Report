-- Seed data for dealer-report application
-- Insert example retailer rules and sample data

-- Insert retailer rules
INSERT INTO retailer_rules (retailer, min_success_rate, min_progress_0930, include_successes) VALUES
  ('Carrefour',     0.95, 0.10, 0),
  ('Intermarché',   0.90, 0.10, 0),
  ('Auchan',        0.90,  NULL, 1),
  ('Leclerc',       0.92, 0.15, 0),
  ('Casino',        0.88, 0.12, 0)
ON DUPLICATE KEY UPDATE
  min_success_rate=VALUES(min_success_rate),
  min_progress_0930=VALUES(min_progress_0930),
  include_successes=VALUES(include_successes);

-- Insert sample crawler runs for testing (last 3 days)
INSERT INTO crawler_runs (retailer, planned_for, started_at, finished_at, status, total_items, ok_items, ko_items) VALUES
  -- Yesterday's data
  ('Carrefour', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 08:00:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 08:30:00'), 'success', 1000, 950, 50),
  ('Carrefour', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 09:00:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 09:25:00'), 'success', 800, 760, 40),
  ('Carrefour', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 10:00:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 10:45:00'), 'success', 1200, 1140, 60),
  
  ('Intermarché', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 08:15:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 08:45:00'), 'success', 600, 540, 60),
  ('Intermarché', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 09:30:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 10:00:00'), 'error', 500, 400, 100),
  
  ('Auchan', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 07:45:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 08:15:00'), 'success', 900, 810, 90),
  ('Auchan', CURDATE() - INTERVAL 1 DAY, CONCAT(CURDATE() - INTERVAL 1 DAY, ' 09:15:00'), CONCAT(CURDATE() - INTERVAL 1 DAY, ' 09:45:00'), 'success', 700, 630, 70),
  
  -- Today's data (some completed before 09:30, some after)
  ('Carrefour', CURDATE(), CONCAT(CURDATE(), ' 08:00:00'), CONCAT(CURDATE(), ' 08:25:00'), 'success', 1100, 1045, 55),
  ('Carrefour', CURDATE(), CONCAT(CURDATE(), ' 09:00:00'), NULL, 'running', NULL, NULL, NULL),
  ('Carrefour', CURDATE(), CONCAT(CURDATE(), ' 10:30:00'), CONCAT(CURDATE(), ' 11:00:00'), 'success', 950, 900, 50),
  
  ('Intermarché', CURDATE(), CONCAT(CURDATE(), ' 08:30:00'), CONCAT(CURDATE(), ' 09:00:00'), 'success', 650, 585, 65),
  ('Intermarché', CURDATE(), CONCAT(CURDATE(), ' 09:45:00'), CONCAT(CURDATE(), ' 10:15:00'), 'error', 400, 320, 80),
  
  ('Auchan', CURDATE(), CONCAT(CURDATE(), ' 07:30:00'), CONCAT(CURDATE(), ' 08:00:00'), 'success', 800, 720, 80),
  ('Auchan', CURDATE(), CONCAT(CURDATE(), ' 09:20:00'), CONCAT(CURDATE(), ' 09:50:00'), 'success', 600, 540, 60),
  
  ('Leclerc', CURDATE(), CONCAT(CURDATE(), ' 08:45:00'), CONCAT(CURDATE(), ' 09:15:00'), 'success', 750, 690, 60),
  ('Leclerc', CURDATE(), CONCAT(CURDATE(), ' 10:00:00'), CONCAT(CURDATE(), ' 10:30:00'), 'error', 500, 400, 100);

-- Insert sample runs plan for today
INSERT INTO runs_plan (plan_date, retailer, expected_total) VALUES
  (CURDATE(), 'Carrefour', 4),
  (CURDATE(), 'Intermarché', 3),
  (CURDATE(), 'Auchan', 3),
  (CURDATE(), 'Leclerc', 2),
  (CURDATE(), 'Casino', 2)
ON DUPLICATE KEY UPDATE
  expected_total=VALUES(expected_total);
