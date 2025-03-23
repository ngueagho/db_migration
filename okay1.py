

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import os

def get_db_engine(db_type, user, password, host, port, database):
    if db_type == "mysql":
        return create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    elif db_type == "postgres":
        return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    elif db_type == "oracle":
        return create_engine(f"oracle+cx_oracle://{user}:{password}@{host}:{port}/{database}")
    elif db_type == "sqlite":
        return create_engine(f"sqlite:///{database}")
    else:
        raise ValueError("Base de données non supportée")

def read_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".csv":
        return pd.read_csv(file_path)
    elif file_extension in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError("Format de fichier non supporté. Utilisez un fichier CSV ou XLSX.")

def import_file_to_db(file_path, table_name, column_mapping, db_type, user, password, host, port, database):
    try:
        df = read_file(file_path)
        missing_cols = [col for col in column_mapping.keys() if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes dans le fichier : {missing_cols}")
        
        df.rename(columns=column_mapping, inplace=True)
        engine = get_db_engine(db_type, user, password, host, port, database)
        
        with engine.connect() as conn:
            for _, row in df.iterrows():
                try:
                    row.to_frame().T.to_sql(table_name, con=engine, if_exists='append', index=False)
                except IntegrityError:
                    print(f"L'ID {row['ID']} existe déjà. Ignoré.")
        
        print("Importation réussie !")
    except Exception as e:
        print(f"Erreur lors de l'importation : {e}")

if __name__ == "__main__":
    file_path = "citizens_data_updated.csv"
    table_name = "CITIZEN"

    column_mapping = {
        "ID_citizen": "ID",
        "NAME_citizen": "NAME",
        "GIVENNAME_citizen": "GIVENNAME",
        "NICKNAME_citizen": "NICKNAME",
        "BIRTHDATE_TECH_citizen": "BIRTHDATE_TECH",
        "BIRTHDATE_citizen": "BIRTHDATE",
        "BIRTHCOUNTRY_citizen": "BIRTHCOUNTRY",
        "BIRTHPLACE_citizen": "BIRTHPLACE",
        "BIRTHDEPT_citizen": "BIRTHDEPT",
        "BIRTHADDRESS_citizen": "BIRTHADDRESS",
        "RESIDENCECOUNTRY_citizen": "RESIDENCECOUNTRY",
        "RESIDENCEDEPT_citizen": "RESIDENCEDEPT",
        "RESIDENCEPLACE_citizen": "RESIDENCEPLACE",
        "RESIDENCEADDRESS_citizen": "RESIDENCEADDRESS",
        "FAMILYORIGINCOUNTRY_citizen": "FAMILYORIGINCOUNTRY",
        "FAMILYORIGINDEPT_citizen": "FAMILYORIGINDEPT",
        "FAMILYORIGINPLACE_citizen": "FAMILYORIGINPLACE",
        "FAMILYORIGINADDRESS_citizen": "FAMILYORIGINADDRESS",
        "GENDER_citizen": "GENDER",
        "NATIONALITY_citizen": "NATIONALITY",
        "IDOCCUPATION_citizen": "IDOCCUPATION",
        "OCCUPATION_citizen": "OCCUPATION",
        "EMPLOYERNAME_citizen": "EMPLOYERNAME",
        "EMPLOYERBOOK_citizen": "EMPLOYERBOOK",
        "PHONENUMBER_citizen": "PHONENUMBER",
        "FATHERNAME_citizen": "FATHERNAME",
        "FATHERBIRTHDATE_citizen": "FATHERBIRTHDATE",
        "MOTHERNAME_citizen": "MOTHERNAME",
        "MOTHERBIRTHDATE_citizen": "MOTHERBIRTHDATE",
        "IDCAMEROONIANREASON_citizen": "IDCAMEROONIANREASON",
        "ENTRYDATE_citizen": "ENTRYDATE",
        "HEIGHT_citizen": "HEIGHT",
        "IDSKINCOLOR_citizen": "IDSKINCOLOR",
        "IDETHNICGROUP_citizen": "IDETHNICGROUP",
        "CREATIONDATE_citizen": "CREATIONDATE",
        "CREATOR_citizen": "CREATOR",
        "MODIFICATIONDATE_citizen": "MODIFICATIONDATE",
        "MODIFIER_citizen": "MODIFIER",
        "POLICENUMBER_citizen": "POLICENUMBER",
        "POLICEMANRANK_citizen": "POLICEMANRANK"
    }

    db_config = {
        "db_type": "mysql",
        "user": "root",
        "password": "",
        "host": "localhost",
        "port": "3306",
        "database": "test"
    }

    import_file_to_db(file_path, table_name, column_mapping, **db_config)
