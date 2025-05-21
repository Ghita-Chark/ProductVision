 create database carrefour;

use carrefour;

mysql> CREATE TABLE admin_actions (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     admin_id INT NOT NULL,
    ->     action_type VARCHAR(100) NOT NULL,
    ->     description TEXT,
    ->     action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -> );

ALTER TABLE produits ADD COLUMN product_name VARCHAR(255);

ALTER TABLE admin_actions ADD COLUMN product_name VARCHAR(255);