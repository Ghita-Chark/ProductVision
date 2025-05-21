Microsoft Windows [version 10.0.22631.5262]
(c) Microsoft Corporation. Tous droits réservés.

C:\Users\Admin>cd C:\MySQL\mysql-5.1\mysql-5.1.30-win32\bin

C:\MySQL\mysql-5.1\mysql-5.1.30-win32\bin>mysql -u root
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 1
Server version: 5.1.30-community MySQL Community Server (GPL)

Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

mysql> use carrefour;
Database changed
mysql> SHOW TABLES;
+---------------------+
| Tables_in_carrefour |
+---------------------+
| admin_actions       |
| produits            |
+---------------------+
2 rows in set (0.02 sec)

mysql> -- Créer la table 'users'
mysql> CREATE TABLE users (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     username VARCHAR(50) UNIQUE NOT NULL,
    ->     password VARCHAR(255) NOT NULL,
    ->     role VARCHAR(20) DEFAULT 'user'
    -> );
Query OK, 0 rows affected (0.02 sec)

mysql> INSERT INTO users (username, password, role) VALUES ('admin1', 'admin123', 'admin');
Query OK, 1 row affected (0.03 sec)

mysql> SELECT * FROM users;
+----+----------+----------+-------+
| id | username | password | role  |
+----+----------+----------+-------+
|  1 | admin1   | admin123 | admin |
+----+----------+----------+-------+
1 row in set (0.01 sec)
