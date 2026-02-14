INSERT INTO products (name, description, price, stock)
SELECT
  CONCAT('Product_', seq) AS name,
  CONCAT('Auto-generated description for product ', seq) AS description,
  ROUND(RAND() * 90000 + 100, 2) AS price,
  FLOOR(RAND() * 200 + 1) AS stock
FROM (
  SELECT @row := @row + 1 AS seq
  FROM information_schema.tables t1,
       information_schema.tables t2,
       (SELECT @row := 0) r
  LIMIT 500
) numbers;
