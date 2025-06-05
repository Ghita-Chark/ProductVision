from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
import os
import pandas as pd
from io import BytesIO
from App.services.data_service import record_admin_action
from App.services.data_service import (
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
    get_admin_action_history
)
from App.dal.db import get_all_products, get_connection
from App.controllers.auth_controller import admin_required ,login_required

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'


@main.route('/')
def index():
    return redirect(url_for('auth.login'))
   # return render_template('auth.login')

@main.route('/upload', methods=['POST'])
@admin_required
def upload():
    file = request.files['csv_file']
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(filepath)
        process_csv(filepath)
        flash("CSV Uploaded and Data Inserted Successfully!")
        return redirect(url_for('main.index'))
    flash("Aucun fichier sélectionné!")
    return redirect(url_for('main.index'))

@main.route('/produits')
def show_products():
    produits = get_all_products()
    kpis = get_kpi_summary()
    return render_template('produits.html', produits=produits, kpis=kpis)

@main.route('/admin')
@admin_required
def admin_dashboard():
    produits = get_all_products()
    kpis = get_kpi_summary()

    stock_labels, stock_values = get_top_stocked_products()
    expensive_labels, expensive_values = get_top_expensive_products()
    stock_dates, stock_time_values = get_stock_over_time()
    department_labels, department_values = get_products_distribution_by_department()
    section_labels, section_values = get_products_distribution_by_section()
    stock_value_labels, stock_value_values = get_stock_value_by_product()

    produits_alertes = get_critical_alerts()
    alert_count = len(produits_alertes)
    historique = get_admin_action_history()

    return render_template('admin_dashboard.html',
                           produits=produits,
                           kpis=kpis,
                           stock_labels=stock_labels,
                           stock_values=stock_values,
                           expensive_labels=expensive_labels,
                           expensive_values=expensive_values,
                           stock_dates=stock_dates,
                           stock_time_values=stock_time_values,
                           department_labels=department_labels,
                           department_values=department_values,
                           section_labels=section_labels,
                           section_values=section_values,
                           stock_value_labels=stock_value_labels,
                           stock_value_values=stock_value_values,
                           produits_alertes=produits_alertes,
                           alert_count=alert_count,
                           historique=historique)
   
    
@main.route('/dashboard')
def dashboard():
    top_stock_labels, top_stock_values = get_top_stocked_products()
    expensive_labels, expensive_values = get_top_expensive_products()
    stock_dates, stock_values = get_stock_over_time()
    department_labels, department_values = get_products_distribution_by_department()
    section_labels, section_values = get_products_distribution_by_section()
    stock_value_labels, stock_value_values = get_stock_value_by_product()
    departement_data = get_products_by_department()
    return render_template('dashboard.html',
                           stock_labels=top_stock_labels,
                           stock_values=top_stock_values,
                           expensive_labels=expensive_labels,
                           expensive_values=expensive_values,
                           stock_dates=stock_dates,
                           stock_time_values=stock_values,
                           department_labels=department_labels,
                           department_values=department_values,
                           section_labels=section_labels,
                           section_values=section_values,
                           stock_value_labels=stock_value_labels,
                           stock_value_values=stock_value_values,
                           departement_data=departement_data)

@main.route('/admin/ajouter', methods=['GET', 'POST'])
@admin_required
def ajouter_produit():
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
            float(request.form['quantity'])
        )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produits 
            (from_date, department, section, barcode, item_num, item_description, purchase_price, selling_price, quantity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        record_admin_action("ajout", request.form['item_description'])
        cursor.close()
        conn.close()

        flash("Produit ajouté avec succès!!")
        return redirect('/admin')

    return render_template('admin_add_product.html')


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
        flash("Produit modifié! ")
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
    flash("Produit supprimé avec succès!")
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
            flash("Fichier CSV importé avec succès !!")
            if session.get('role') == 'admin':
                return redirect(url_for('main.admin_dashboard'))  
                return redirect(url_for('main.show_products')) 
        else:
            flash("Veuillez sélectionner un fichier CSV!!")

    return render_template('import_csv.html')  
