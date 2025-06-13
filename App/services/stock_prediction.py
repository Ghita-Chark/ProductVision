# app/services/stock_prediction_service.py
import pandas as pd
from App.dal.db import get_connection

def predict_future_stock(nom_produit):
    conn = get_connection()
    df = pd.read_sql("SELECT from_date, item_description, quantity FROM produits", conn)
    conn.close()

    df = df[df["item_description"] == nom_produit]
    if df.empty:
        return None

    df["from_date"] = pd.to_datetime(df["from_date"], errors='coerce')
    df = df.dropna(subset=["from_date"])
    df = df.groupby("from_date")["quantity"].sum().reset_index()
    df = df.sort_values("from_date")

    # Remplissage des dates manquantes
    df.set_index("from_date", inplace=True)
    df = df.asfreq("D", fill_value=0)
    df.reset_index(inplace=True)

    # Ajout d'une tendance linéaire simple
    df["tendance"] = df["quantity"].rolling(window=3, min_periods=1).mean()
    df["prediction"] = df["tendance"].shift(1).fillna(method="bfill")

    return {
        "dates": df["from_date"].astype(str).tolist()[-15:],  # dernières dates
        "values": df["prediction"].tolist()[-15:]
    }
