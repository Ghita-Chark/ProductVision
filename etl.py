import glob as g
import pandas as pd
from datetime import datetime
import os
from database import DatabaseConnector 


# Instancier la connexion
db_connector = DatabaseConnector()
engine = db_connector.get_engine()



# Extraction
def extract_from_csv(file):
    """Extract data from a CSV file."""
    df = pd.read_csv(file)
    return df

def extract_from_json(file):
    """Extract data from a JSON file."""
    df = pd.read_json(file, lines=True)
    return df

def extract():
    extracted_data = pd.DataFrame(columns = ['from_date', 'department', 'section', 'barcode', 'item_num', 'item_description', 'purshase_price', 'selling_price', 'quantity'])
    
    for i in g.glob("Raw_Data/*.csv"):
        extracted_data = pd.concat([extracted_data, extract_from_csv(i)], ignore_index=True)

        
    for i in g.glob("Raw_Data/*.json"):
        extracted_data = pd.concat([extracted_data, extract_from_json(i)], ignore_index=True)

        
    return extracted_data

# Transformation

def transform(data):
    """Transform the data."""
   
    
    # Fill missing values with 0
    data.fillna(0, inplace=True)
    
    data['purshase_price'] = round(data['purshase_price'], 2)
    data['selling_price'] = round(data['selling_price'], 2)
    
    # Convert 'quantity' to integer
    data['quantity'] = data['quantity'].astype(int)
    
    return data

def load(table_name, data_to_load):
    if engine is not None:
        try:
            data_to_load.to_sql(table_name, engine, if_exists='append', index=False)
            print(f" Données insérées dans la table '{table_name}' avec succès !")
        except Exception as e:
            print(f" Erreur lors de l'insertion des données : {e}")
    else:
        print(" Impossible de charger les données : Pas de connexion à la base.")
        
        
if __name__ == "__main__":
    print("Extraction des données...")
    extracted_data = extract()
    
    print("transformation des données...")
    transformed_data = transform(extracted_data)
    
    print("Chargement des données dans SQL Server...")
    load("product_db", transformed_data)