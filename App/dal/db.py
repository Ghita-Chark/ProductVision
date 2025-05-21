import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def insert_data(data):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO produits 
        (from_date, department, section, barcode, item_num, 
         item_description, purchase_price, selling_price, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        print("Exemple de ligne à insérer :", data[0])  # Debug
        cursor.executemany(query, data)
        conn.commit()
        print("Données insérées avec succès.")
    except Exception as e:
        print("Erreur lors de l'insertion :", e)
    finally:
        cursor.close()
        conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produits")
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results

