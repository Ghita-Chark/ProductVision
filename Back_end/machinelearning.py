import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

from datetime import datetime

# Charger le dataset
file_path = "C:/Users/Admin/Desktop/PFA PROJECT/Carrefour Dataset.csv"
df = pd.read_csv(file_path, encoding="ISO-8859-1")

# Conversion de la date
df['from_date'] = pd.to_datetime(df['from_date'], format='%d-%b')
df['year'] = 2024  # Ajouter une année par défaut pour éviter les erreurs
df['from_date'] = pd.to_datetime(df[['year', 'from_date']].apply(lambda x: f"{x['year']}-{x['from_date'].month}-{x['from_date'].day}", axis=1))

# Sélection d'un produit spécifique
product = "CHICKEN BREAST FILLET/KG"
df_product = df[df['item_description'] == product]

# Agréger par mois
df_product = df_product.resample('M', on='from_date').sum()['quantity']

# Création du modèle SARIMA
model = SARIMAX(df_product, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
result = model.fit()

# Faire une prévision pour les 6 prochains mois
future_dates = pd.date_range(start=df_product.index[-1], periods=7, freq='M')[1:]
predictions = result.forecast(steps=6)

# Affichage des résultats
plt.figure(figsize=(10,5))
plt.plot(df_product.index, df_product, label='Ventes réelles', marker='o')
plt.plot(future_dates, predictions, label='Prévisions', linestyle='dashed', marker='s', color='red')
plt.xlabel('Date')
plt.ylabel('Quantité vendue')
plt.legend()
plt.title(f'Prévision des ventes pour {product}')
plt.grid()
plt.savefig('forecast_sales.png')  # Sauvegarde du graphique
plt.show()

# Afficher les prévisions
print(predictions)
