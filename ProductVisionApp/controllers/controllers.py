from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import os
import pandas as pd
from io import BytesIO
from app.services.data_service import record_admin_action
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
    get_admin_action_history
)
from app.dal.db import get_all_products, get_connection

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    file = request.files['csv_file']
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(filepath)
        process_csv(filepath)
        return "CSV Uploaded and Data Inserted!"
    return redirect(url_for('main.index'))

@main.route('/produits')
def show_products():
    produits = get_all_products()
    kpis = get_kpi_summary()
    return render_template('produits.html', produits=produits, kpis=kpis)
