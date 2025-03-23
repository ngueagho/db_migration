import pandas as pd
import psycopg2
import logging
from psycopg2.extras import execute_values

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration de la base de données
DB_CONFIG = {
    "dbname": "verify",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5432"
}

# Définition du mapping entre les colonnes du CSV et celles de la table
COLUMN_MAPPING = {
    "id_e": "id",
    "nom_e": "nom",
    "age_e": "age",
}

PRIMARY_KEY = "id"  # Clé primaire de la table
TABLE_NAME = "etudiant"  # Nom de la table
CSV_FILE_PATH = "etudiants.csv"

# Connexion à la base de données
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

def get_existing_records(primary_keys):
    """Récupère les enregistrements existants dans la base de données."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE {PRIMARY_KEY} = ANY(%s)"
    cursor.execute(query, (list(primary_keys),))
    return {row[0]: row for row in cursor.fetchall()}  # Dictionnaire clé primaire -> tuple

def validate_data(df):
    """Valide les types de données avant l'importation."""
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')  # Convertir en nombre
        if df['age'].isnull().any():
            raise ValueError("Erreur de conversion : certaines valeurs de 'age' ne sont pas des nombres valides.")

def import_csv_to_postgres():
    logging.info("Chargement du fichier CSV...")
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Vérifier les colonnes requises
    missing_columns = [col for col in COLUMN_MAPPING.keys() if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Colonnes manquantes dans le CSV: {missing_columns}")
    
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    
    if PRIMARY_KEY in df.columns:
        df.drop_duplicates(subset=[PRIMARY_KEY], keep="last", inplace=True)
    
    validate_data(df)
    
    existing_records = get_existing_records(df[PRIMARY_KEY].tolist())
    conflicts = df[df[PRIMARY_KEY].isin(existing_records.keys())]
    
    if not conflicts.empty:
        logging.warning("Conflits détectés entre le fichier CSV et la base de données :")
        for index, row in conflicts.iterrows():
            logging.warning(f"Dans le fichier CSV : {row.to_dict()}")
            logging.warning(f"Dans la base de données : {existing_records[row[PRIMARY_KEY]]}")
        user_choice = input("Voulez-vous (I) Ignorer, (U) Mettre à jour ou (A) Annuler l'importation ? ")
        if user_choice.upper() == "A":
            logging.info("Importation annulée.")
            return
        elif user_choice.upper() == "I":
            df = df[~df[PRIMARY_KEY].isin(existing_records.keys())]
    
    columns = list(COLUMN_MAPPING.values())
    values = [tuple(row) for row in df[columns].to_numpy()]
    
    insert_query = f"""
        INSERT INTO {TABLE_NAME} ({', '.join(columns)})
        VALUES %s
        ON CONFLICT ({PRIMARY_KEY}) DO UPDATE
        SET {', '.join(f'{col} = EXCLUDED.{col}' for col in columns if col != PRIMARY_KEY)}
    """
    
    with conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, values)
            logging.info("Importation réussie !")

try:
    import_csv_to_postgres()
except Exception as e:
    logging.error(f"Erreur: {e}")
finally:
    cursor.close()
    conn.close()
