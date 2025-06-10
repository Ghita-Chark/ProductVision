from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session, jsonify
import os
import pandas as pd
from io import BytesIO
import plotly.graph_objs as go
from app.services.data_service import (
    process_csv,
    get_kpi_summary,
    get_top_expensive_products,
    get_top_stocked_products,
    get_stock_over_time,
    get_products_distribution_by_department,
    get_products_distribution_by_section,
    get_stock_value_by_product,
    get_products_by_department,
    get_critical_alerts,
    get_rupture_products_only_names,
    get_admin_action_history,
    get_all_products,
    get_all_products_grouped,
    record_admin_action
)
from app.dal.db import get_connection
from app.controllers.auth_controller import admin_required, login_required
from app.services.stock_prediction_service import predict_future_stock

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'

@main.route('/')
def home():
    return render_template('home.html')


@main.route('/upload', methods=['POST'])
@admin_required
def upload():
    file = request.files['csv_file']
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(filepath)
        process_csv(filepath)
        flash("CSV Uploaded and Data Inserted ✅")
    else:
        flash("Aucun fichier sélectionné ❌")
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin')
@admin_required
def admin_dashboard():
    produits = get_all_products_grouped()
    kpis = get_kpi_summary()
    return render_template('admin_dashboard.html',
                           produits=produits,
                           kpis=kpis,
                           stock_labels=get_top_stocked_products()[0],
                           stock_values=get_top_stocked_products()[1],
                           expensive_labels=get_top_expensive_products()[0],
                           expensive_values=get_top_expensive_products()[1],
                           stock_dates=get_stock_over_time()[0],
                           stock_time_values=get_stock_over_time()[1],
                           department_labels=get_products_distribution_by_department()[0],
                           department_values=get_products_distribution_by_department()[1],
                           section_labels=get_products_distribution_by_section()[0],
                           section_values=get_products_distribution_by_section()[1],
                           stock_value_labels=get_stock_value_by_product()[0],
                           stock_value_values=get_stock_value_by_product()[1],
                           produits_alertes=get_critical_alerts(),
                           alert_count=len(get_critical_alerts()),
                           historique=get_admin_action_history())


@main.route('/statistiques')
@admin_required
def statistiques_page():
    return render_template('dashboard.html',
        kpis=get_kpi_summary(),
        stock_labels=get_top_stocked_products()[0],
        stock_values=get_top_stocked_products()[1],
        expensive_labels=get_top_expensive_products()[0],
        expensive_values=get_top_expensive_products()[1],
        stock_dates=get_stock_over_time()[0],
        stock_time_values=get_stock_over_time()[1],
        department_labels=get_products_distribution_by_department()[0],
        department_values=get_products_distribution_by_department()[1],
        section_labels=get_products_distribution_by_section()[0],
        section_values=get_products_distribution_by_section()[1],
        stock_value_labels=get_stock_value_by_product()[0],
        stock_value_values=get_stock_value_by_product()[1],
        departement_data=get_products_by_department()
    )


@main.route('/stock')
@admin_required
def stock_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.item_description, s.quantity_initiale,
               IFNULL(SUM(p.quantity), 0) AS quantity_vendue,
               (s.quantity_initiale - IFNULL(SUM(p.quantity), 0)) AS stock_restant
        FROM stock s
        LEFT JOIN produits p ON s.item_description = p.item_description
        GROUP BY s.item_description, s.quantity_initiale
    """)
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()

    # ajoute alert_count pour éviter l’erreur jinja2
    produits_alertes = get_critical_alerts()
    alert_count = len(produits_alertes)

    return render_template("stock.html", stocks=stocks, alert_count=alert_count)


@main.route('/export/stock')
@admin_required
def export_stock():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.item_description, s.quantity_initiale,
               IFNULL(SUM(p.quantity), 0) AS quantity_vendue,
               (s.quantity_initiale - IFNULL(SUM(p.quantity), 0)) AS stock_restant
        FROM stock s
        LEFT JOIN produits p ON s.item_description = p.item_description
        GROUP BY s.item_description, s.quantity_initiale
    """)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="etat_stock.xlsx", as_attachment=True)




@main.route('/admin/ajouter', methods=['GET', 'POST'])
@admin_required
def ajouter_produit():
    from app.services.data_service import get_critical_alerts  # si pas déjà importé
    if request.method == 'POST':
        item_description = request.form['item_description']
        quantity_ajoutee = float(request.form['quantity'])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, quantity_initiale FROM stock WHERE item_description = %s", (item_description,))
        stock_entry = cursor.fetchone()

        if stock_entry:
            nouvelle_quantite = stock_entry[1] + quantity_ajoutee
            cursor.execute("UPDATE stock SET quantity_initiale = %s WHERE id = %s", (nouvelle_quantite, stock_entry[0]))
        else:
            cursor.execute("""
                INSERT INTO stock (item_description, quantity_initiale, date_ajout)
                VALUES (%s, %s, CURDATE())
            """, (item_description, quantity_ajoutee))

        record_admin_action("ajout_stock", item_description)
        conn.commit()
        cursor.close()
        conn.close()
        flash("Produit ajouté au stock ✅")
        return redirect('/stock')
    
    produits_alertes = get_critical_alerts()
    alert_count = len(produits_alertes)

    return render_template('admin_add_product.html', alert_count=alert_count)


@main.route('/admin/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required
def modifier_produit(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = (
            request.form['from_date'],
            request.form['department'],
            int(request.form['section']),
            int(request.form['barcode']),
            int(request.form['item_num']),
            request.form['item_description'],
            float(request.form['purchase_price']),
            float(request.form['selling_price']),
            float(request.form['quantity']),
            id
        )
        cursor.execute("""
            UPDATE produits SET 
            from_date=%s, department=%s, section=%s, barcode=%s, item_num=%s,
            item_description=%s, purchase_price=%s, selling_price=%s, quantity=%s
            WHERE id=%s
        """, data)
        conn.commit()
        record_admin_action("modification", request.form['item_description'])
        cursor.close()
        conn.close()
        flash("Produit modifié ✅")
        return redirect('/admin')

    cursor.execute("SELECT * FROM produits WHERE id=%s", (id,))
    produit = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin_edit_product.html', produit=produit)


@main.route('/admin/supprimer/<int:id>')
@admin_required
def supprimer_produit(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_description FROM produits WHERE id=%s", (id,))
    result = cursor.fetchone()
    product_name = result[0] if result else "Inconnu"

    cursor.execute("DELETE FROM produits WHERE id=%s", (id,))
    conn.commit()
    record_admin_action("suppression", product_name)
    cursor.close()
    conn.close()
    flash("Produit supprimé ✅")
    return redirect('/admin')


@main.route('/export/produits')
@admin_required
def export_produits():
    produits = get_all_products()
    df = pd.DataFrame(produits)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="produits.xlsx", as_attachment=True)


@main.route('/export/historique')
@admin_required
def export_historique():
    historique = get_admin_action_history()
    df = pd.DataFrame(historique)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="historique_admin.xlsx", as_attachment=True)


@main.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        file = request.files['csv_file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            process_csv(filepath)
            flash("Fichier CSV importé avec succès ✅")
            if session.get('role') == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.show_products'))
        else:
            flash("Veuillez sélectionner un fichier CSV ❌")

    return render_template('import_csv.html')


@main.route('/admin/prediction', methods=["GET", "POST"])
@admin_required
def prediction_page():
    produits = get_all_products()
    unique_names = sorted(set(p["item_description"] for p in produits if p["item_description"]))
    selected_product = None
    plot_div = None

    if request.method == "POST":
        selected_product = request.form.get("produit")
        if selected_product:
            prediction_data = predict_future_stock(selected_product)
            if prediction_data:
                trace = go.Scatter(x=prediction_data["dates"], y=prediction_data["values"],
                                   mode="lines+markers", name="Stock prédit")
                layout = go.Layout(title=f"Évolution du stock prévu : {selected_product}",
                                   xaxis=dict(title="Date"), yaxis=dict(title="Quantité"))
                fig = go.Figure(data=[trace], layout=layout)
                plot_div = fig.to_html(full_html=False)

    return render_template("predict_stock.html", produits=unique_names,
                           selected_product=selected_product, plot_div=plot_div)


@main.route("/api/products")
def api_get_products():
    produits = get_all_products()
    unique_names = sorted(set(p["item_description"] for p in produits if p["item_description"]))
    return jsonify({"products": unique_names})





@main.route('/assistant')
@admin_required
def assistant_page():
    alert_count = len(get_critical_alerts())
    return render_template("chat_admin.html", alert_count=alert_count)



@main.route("/alertes")
@admin_required
def alertes_page():
    alertes = get_rupture_products_only_names()
    actions = get_admin_action_history()
    return render_template("alertes.html", alertes=alertes, actions=actions, alert_count=len(alertes))




