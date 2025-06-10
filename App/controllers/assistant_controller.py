from flask import Blueprint, request, jsonify
import pandas as pd
import spacy
import os

# ✅ Correction du nom du blueprint
assistant_bp = Blueprint('assistant', __name__)

# 🔎 Chargement du dataset
dataset_path = "uploads/Carrefour_Dataset.csv"
if os.path.exists(dataset_path):
    df = pd.read_csv(dataset_path)
    print("✅ Dataset chargé avec succès.")
else:
    print(f"❌ Dataset introuvable : {dataset_path}")
    df = pd.DataFrame()

# 📚 Chargement du modèle spaCy français
try:
    nlp = spacy.load("fr_core_news_md")
except Exception as e:
    print("❌ Erreur de chargement NLP :", e)
    nlp = None

# 🔍 Détection d’intention à partir de la question utilisateur
def detect_intention(question):
    question = question.lower()
    if "répartition" in question and "département" in question:
        return "graph_repartition"
    if "top 5" in question and ("graph" in question or "graphique" in question):
        return "graph_top5"
    if "prix moyen" in question and ("graph" in question or "graphique" in question):
        return "graph_prix_moyen"
    if "produit" in question and any(w in question for w in ["total", "nombre", "combien"]):
        return "produit_total"
    if "rupture" in question or "stock" in question:
        return "produit_rupture"
    if "plus cher" in question or "prix élevé" in question:
        return "produit_plus_cher"
    if "plus vendu" in question or "quantité" in question or "vendu" in question or "top 5" in question:
        return "top5_quantite"
    if "valeur" in question and "stock" in question:
        return "valeur_stock"
    if "moins de" in question or "bon marché" in question or "pas cher" in question:
        return "produit_pas_cher"
    if "produits" in question and "dans" in question:
        return "produits_par_departement"
    if "prix moyen" in question:
        return "prix_moyen_par_departement"
    if "recommandation" in question or "améliorer les ventes" in question or "optimiser" in question:
        return "recommandation"
    return "inconnu"

@assistant_bp.route("/api/assistant", methods=["POST"])
def assistant():
    if df.empty:
        return jsonify({"response": "❌ Aucune donnée disponible."})

    data = request.json or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"response": "❌ Merci de poser une question valide."})

    print("🧠 Question reçue :", question)

    intention = detect_intention(question)

    if intention == "produit_total":
        total = df["item_description"].nunique()
        return jsonify({"response": f"Il y a {total} produits uniques."})

    elif intention == "produit_rupture":
        ruptures = df[df["quantity"] == 0]
        nb = ruptures["item_description"].nunique()
        return jsonify({"response": f"{nb} produits sont en rupture de stock."})

    elif intention == "produit_plus_cher":
        if df.empty or "selling_price" not in df:
            return jsonify({"response": "❌ Données incomplètes."})
        produit = df.loc[df["selling_price"].idxmax()]["item_description"]
        prix = df["selling_price"].max()
        return jsonify({"response": f"Le produit le plus cher est '{produit}' ({prix} MAD)."})

    elif intention == "valeur_stock":
        if "selling_price" not in df or "quantity" not in df:
            return jsonify({"response": "❌ Données insuffisantes pour calculer la valeur du stock."})
        df["valeur_stock"] = df["selling_price"] * df["quantity"]
        total = df["valeur_stock"].sum()
        return jsonify({"response": f"La valeur totale du stock est de {round(total, 2)} MAD."})

    elif intention == "produit_pas_cher":
        bon_marche = df[df["selling_price"] < 10]["item_description"].unique()
        produits = ", ".join(bon_marche[:5]) + ("..." if len(bon_marche) > 5 else "")
        return jsonify({"response": f"Exemples de produits à moins de 10 MAD : {produits}"})

    elif intention == "produits_par_departement":
        if "dans" in question:
            departement_question = question.split("dans")[-1].strip()
            matching = df[df["department"].str.lower().str.contains(departement_question)]
            count = matching["item_description"].nunique()
            if count > 0:
                return jsonify({"response": f"Il y a {count} produits dans le département '{departement_question.title()}'."})
            else:
                return jsonify({"response": f"❌ Aucun produit trouvé pour le département '{departement_question}'."})

    elif intention == "prix_moyen_par_departement":
        if "graph" in question or "graphique" in question:
            return jsonify({"response": "chart:prix_moyen"})
        moyennes = df.groupby("department")["selling_price"].mean().sort_values(ascending=False)
        top = moyennes.head(5).round(2).to_dict()
        msg = "Prix moyen de vente par département (top 5) :\n" + "\n".join([f"{k}: {v} MAD" for k, v in top.items()])
        return jsonify({"response": msg})

    elif intention == "top5_quantite":
        if "graph" in question or "graphique" in question:
            return jsonify({"response": "chart:top5"})
        top5 = df.sort_values(by="quantity", ascending=False).head(5)
        top_liste = [f"{row['item_description']} ({row['quantity']})" for _, row in top5.iterrows()]
        return jsonify({"response": "Top 5 produits par quantité :\n" + "\n".join(top_liste)})

    elif intention == "graph_repartition":
        return jsonify({"response": "chart:departement"})

    elif intention == "graph_top5":
        return jsonify({"response": "chart:top5"})

    elif intention == "graph_prix_moyen":
        return jsonify({"response": "chart:prix_moyen"})

    elif intention == "recommandation":
        recommandations = []

        # 💡 Produit cher et peu en stock
        chers_peu = df[(df["selling_price"] > df["selling_price"].mean()) & (df["quantity"] < df["quantity"].mean())]
        if not chers_peu.empty:
            produit = chers_peu.iloc[0]["item_description"]
            recommandations.append(f"💡 Le produit '{produit}' est cher mais se vend peu. Baisser le prix pourrait booster les ventes.")

        # 📦 Surstocks
        seuil = df["quantity"].mean() * 2
        surstock = df[df["quantity"] > seuil]
        if not surstock.empty:
            noms = ", ".join(surstock["item_description"].head(3).tolist())
            recommandations.append(f"📦 Ces produits sont surstockés : {noms}. Lancez une promo pour écouler le stock.")

        # 🔥 Meilleures ventes
        top = df.sort_values(by="quantity", ascending=False).head(3)["item_description"].tolist()
        recommandations.append(f"🔥 Les meilleurs vendeurs : {', '.join(top)}. Pensez à les mettre en avant !")

        return jsonify({"response": "\n".join(recommandations)})

    return jsonify({"response": "❌ Je n'ai pas compris. Essayez 'top 5', 'valeur stock', 'prix moyen', 'recommandation', etc."})

# ============ ROUTES GRAPHIQUES ============

@assistant_bp.route("/api/assistant/chart/departement", methods=["GET"])
def chart_repartition_departement():
    if df.empty:
        return jsonify({"labels": [], "values": []})
    counts = df["department"].value_counts()
    return jsonify({
        "labels": counts.index.tolist(),
        "values": counts.values.tolist()
    })

@assistant_bp.route("/api/assistant/chart/top5", methods=["GET"])
def chart_top5():
    if df.empty:
        return jsonify({"labels": [], "values": []})
    top5 = df.sort_values(by="quantity", ascending=False).head(5)
    return jsonify({
        "labels": top5["item_description"].tolist(),
        "values": top5["quantity"].tolist()
    })

@assistant_bp.route("/api/assistant/chart/prix_moyen", methods=["GET"])
def chart_prix_moyen():
    if df.empty:
        return jsonify({"labels": [], "values": []})
    grouped = df.groupby("department")["selling_price"].mean().sort_values(ascending=False).head(5)
    return jsonify({
        "labels": grouped.index.tolist(),
        "values": grouped.round(2).tolist()
    })
