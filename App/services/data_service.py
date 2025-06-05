import pandas as pd
from App.dal.db import insert_data, get_all_products, get_connection


def process_csv(file_path):
    df = pd.read_csv(file_path)

    df = df.rename(columns={'purshase_price': 'purchase_price'})
    df = df.drop_duplicates()
    df = df.dropna()

    numeric_cols = ['section', 'barcode', 'item_num', 'purchase_price', 'selling_price', 'quantity']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    df['from_date'] = pd.to_datetime(df['from_date'], errors='coerce')
    df['from_date'] = df['from_date'].apply(lambda x: x.replace(year=2024) if pd.notnull(x) else x)
    df['from_date'] = df['from_date'].dt.strftime('%Y-%m-%d')
    df = df.dropna(subset=['from_date'])

    expected_columns = ['from_date', 'department', 'section', 'barcode', 'item_num',
                        'item_description', 'purchase_price', 'selling_price', 'quantity']

    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        print("Colonnes manquantes :", missing)
        return

    records = df[expected_columns].values.tolist()

    if len(records) == 0:
        print("Aucun enregistrement valide à insérer.")
        return
    else:
        print(f"{len(records)} enregistrements prêts à l'insertion.")
        print("Exemple :", records[0])

    insert_data(records)


def get_kpi_summary():
    produits = get_all_products()
    df = pd.DataFrame(produits)

    if df.empty:
        return {
            'total_produits': 0,
            'stock_total': 0,
            'prix_moyen_vente': 0,
            'produit_plus_cher': '',
            'produit_moins_cher': '',
            'produits_en_rupture': 0
        }

    total_produits = len(df)
    stock_total = df['quantity'].sum()
    prix_moyen_vente = df['selling_price'].mean()
    produit_plus_cher = df.loc[df['selling_price'].idxmax()]['item_description']
    produit_moins_cher = df.loc[df['selling_price'].idxmin()]['item_description']
    produits_en_rupture = df[df['quantity'] == 0].shape[0]

    return {
        'total_produits': total_produits,
        'stock_total': stock_total,
        'prix_moyen_vente': prix_moyen_vente,
        'produit_plus_cher': produit_plus_cher,
        'produit_moins_cher': produit_moins_cher,
        'produits_en_rupture': produits_en_rupture
    }


def get_top_stocked_products(limit=10):
    produits = get_all_products()
    df = pd.DataFrame(produits)

    top_df = df.groupby('item_description')['quantity'].sum().sort_values(ascending=False).head(limit)
    return top_df.index.tolist(), top_df.values.tolist()


def get_top_expensive_products(limit=10):
    produits = get_all_products()
    df = pd.DataFrame(produits)

    top_df = df[['item_description', 'selling_price']].drop_duplicates()
    top_df = top_df.sort_values(by='selling_price', ascending=False).head(limit)

    return top_df['item_description'].tolist(), top_df['selling_price'].tolist()


def get_stock_over_time():
    produits = get_all_products()
    df = pd.DataFrame(produits)

    df['from_date'] = pd.to_datetime(df['from_date'], errors='coerce')
    df = df.dropna(subset=['from_date'])

    stock_over_time = df.groupby('from_date')['quantity'].sum().sort_index()

    dates = stock_over_time.index.strftime('%Y-%m-%d').tolist()
    values = stock_over_time.values.tolist()

    return dates, values


def get_products_distribution_by_department():
    produits = get_all_products()
    df = pd.DataFrame(produits)

    distribution = df['department'].value_counts()
    labels = distribution.index.astype(str).tolist()
    values = distribution.values.tolist()

    return labels, values


def get_products_distribution_by_section():
    produits = get_all_products()
    df = pd.DataFrame(produits)

    distribution = df['section'].value_counts()
    labels = distribution.index.astype(str).tolist()
    values = distribution.values.tolist()

    return labels, values


def get_stock_value_by_product(limit=10):
    produits = get_all_products()
    df = pd.DataFrame(produits)

    df['valeur_stock'] = df['quantity'] * df['selling_price']
    top_df = df.groupby('item_description')['valeur_stock'].sum().sort_values(ascending=False).head(limit)

    return top_df.index.tolist(), top_df.values.tolist()


def get_products_by_department():
    produits = get_all_products()
    df = pd.DataFrame(produits)

    grouped = df.groupby(['department', 'item_description'])['quantity'].sum().reset_index()
    return grouped.to_dict(orient='records')



def get_critical_alerts(threshold=5):
    produits = get_all_products()
    df = pd.DataFrame(produits)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')  
    df = df[df['quantity'] <= threshold]
    return df.to_dict(orient='records')



def get_admin_action_history(limit=10):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT action_type, product_name, action_date
        FROM admin_actions
        ORDER BY action_date DESC
        LIMIT %s
    """, (limit,))
    actions = cursor.fetchall()
    cursor.close()
    conn.close()
    return actions


from app.dal.db import get_connection

def record_admin_action(action_type, product_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO admin_actions (action_type, product_name)
        VALUES (%s, %s)
    """, (action_type, product_name))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Action enregistrée : {action_type}, produit : {product_name}")




