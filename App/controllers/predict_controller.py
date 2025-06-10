from flask import Blueprint, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import os
import plotly.graph_objs as go
import plotly.offline as pyo

predict_bp = Blueprint("predict", __name__)

# 🔎 Chargement sécurisé du dataset
dataset_path = "uploads/Carrefour_Dataset.csv"
if os.path.exists(dataset_path):
    df = pd.read_csv(dataset_path)
    print("✅ Dataset chargé avec succès.")
else:
    print(f"❌ Dataset introuvable : {dataset_path}")
    df = pd.DataFrame()  # Dataset vide

# 📈 Route API prédiction JSON (optionnelle pour appels JS)
@predict_bp.route("/api/predict-stock", methods=["GET"])
def predict_stock():
    product_name = request.args.get("product")
    if not product_name:
        return jsonify({"error": "Le paramètre 'product' est requis."}), 400

    if df.empty:
        return jsonify({"error": "Le dataset est introuvable ou vide."}), 500

    data = df[df["item_description"] == product_name].copy()

    if data.empty or data["from_date"].nunique() < 3:
        return jsonify({"error": "Pas assez de données historiques pour ce produit."}), 400

    data["from_date"] = pd.to_datetime(data["from_date"])
    daily_stock = data.groupby("from_date")["quantity"].sum().reset_index()
    daily_stock["day"] = (daily_stock["from_date"] - daily_stock["from_date"].min()).dt.days
    X = daily_stock[["day"]]
    y = daily_stock["quantity"]

    model = LinearRegression()
    model.fit(X, y)

    last_day = daily_stock["day"].max()
    future_days = np.arange(last_day + 1, last_day + 8)
    future_dates = [daily_stock["from_date"].max() + timedelta(days=i) for i in range(1, 8)]
    future_preds = model.predict(future_days.reshape(-1, 1)).round(2)

    return jsonify({
        "dates": [d.strftime("%Y-%m-%d") for d in future_dates],
        "values": future_preds.tolist()
    })


# 🖥️ Route HTML avec formulaire + graphique Plotly
@predict_bp.route("/prediction", methods=["GET", "POST"])
def prediction_page():
    produits = sorted(df["item_description"].unique()) if not df.empty else []
    plot_div = None

    if request.method == "POST":
        produit = request.form.get("produit")
        data = df[df["item_description"] == produit].copy()

        if not data.empty and data["from_date"].nunique() >= 3:
            data["from_date"] = pd.to_datetime(data["from_date"])
            daily_stock = data.groupby("from_date")["quantity"].sum().reset_index()

            daily_stock["day"] = (daily_stock["from_date"] - daily_stock["from_date"].min()).dt.days
            X = daily_stock[["day"]]
            y = daily_stock["quantity"]

            model = LinearRegression()
            model.fit(X, y)

            last_day = daily_stock["day"].max()
            future_days = np.arange(last_day + 1, last_day + 8)
            future_dates = [daily_stock["from_date"].max() + timedelta(days=i) for i in range(1, 8)]
            future_preds = model.predict(future_days.reshape(-1, 1)).round(2)

            trace1 = go.Scatter(x=daily_stock["from_date"], y=y, mode='lines+markers', name='Historique')
            trace2 = go.Scatter(x=future_dates, y=future_preds, mode='lines+markers', name='Prévision')
            layout = go.Layout(title="📊 Prédiction du stock", xaxis=dict(title="Date"), yaxis=dict(title="Quantité"))

            fig = go.Figure(data=[trace1, trace2], layout=layout)
            plot_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    return render_template("predict_stock.html", produits=produits, plot_div=plot_div)
