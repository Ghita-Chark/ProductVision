Microsoft Windows [version 10.0.22631.5189]
(c) Microsoft Corporation. Tous droits réservés.

C:\Users\Admin>cd C:\MySQL\mysql-5.1\mysql-5.1.30-win32\bin

C:\MySQL\mysql-5.1\mysql-5.1.30-win32\bin>mysql -u root
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 2
Server version: 5.1.30-community MySQL Community Server (GPL)

Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

mysql> CREATE TABLE produits (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     from_date DATE NOT NULL,
    ->     department VARCHAR(100),
    ->     section VARCHAR(100),
    ->     barcode VARCHAR(50),
    ->     item_num VARCHAR(50),
    ->     item_description TEXT,
    ->     purchase_price DECIMAL(10, 2),
    ->     selling_price DECIMAL(10, 2),
    ->     quantity INT
    -> );
ERROR 1046 (3D000): No database selected
mysql> create database carrefour;
Query OK, 1 row affected (0.02 sec)

mysql> use carrefour;
Database changed
mysql> CREATE TABLE produits (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     from_date DATE NOT NULL,
    ->     department VARCHAR(100),
    ->     section VARCHAR(100),
    ->     barcode VARCHAR(50),
    ->     item_num VARCHAR(50),
    ->     item_description TEXT,
    ->     purchase_price DECIMAL(10, 2),
    ->     selling_price DECIMAL(10, 2),
    ->     quantity INT
    -> );
Query OK, 0 rows affected (0.00 sec)

mysql> CREATE TABLE admin_actions (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     admin_id INT NOT NULL,
    ->     action_type VARCHAR(100) NOT NULL,
    ->     description TEXT,
    ->     action_date DATETIME DEFAULT CURRENT_TIMESTAMP
    -> );
ERROR 1067 (42000): Invalid default value for 'action_date'
mysql> CREATE TABLE admin_actions (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     admin_id INT NOT NULL,
    ->     action_type VARCHAR(100) NOT NULL,
    ->     description TEXT,
    ->     action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -> );
Query OK, 0 rows affected (0.01 sec)

mysql> ALTER TABLE produits ADD COLUMN product_name VARCHAR(255);
Query OK, 1726 rows affected (0.02 sec)
Records: 1726  Duplicates: 0  Warnings: 0

mysql> ALTER TABLE admin_actions DROP COLUMN description;
Query OK, 0 rows affected (0.00 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> ALTER TABLE admin_actions ADD COLUMN product_name VARCHAR(255);
Query OK, 0 rows affected (0.02 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql>



