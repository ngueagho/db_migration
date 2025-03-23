# import pandas as pd
# from sqlalchemy import create_engine
# from sqlalchemy.exc import IntegrityError
# import os

# def get_db_engine(db_type, user, password, host, port, database):
#     if db_type == "mysql":
#         return create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
#     elif db_type == "postgresql" or db_type == "postgres":  # Correction ici
#         return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
#     elif db_type == "oracle":
#         return create_engine(f"oracle+cx_oracle://{user}:{password}@{host}:{port}/{database}")
#     elif db_type == "sqlite":
#         return create_engine(f"sqlite:///{database}")
#     else:
#         raise ValueError(f"Base de données non supportée : {db_type}")

# def read_file(file_path):
#     file_extension = os.path.splitext(file_path)[1].lower()
#     if file_extension == ".csv":
#         return pd.read_csv(file_path)
#     elif file_extension in [".xls", ".xlsx"]:
#         return pd.read_excel(file_path)
#     else:
#         raise ValueError("Format de fichier non supporté. Utilisez un fichier CSV ou XLSX.")

# def import_file_to_db(file_path, table_name, column_mapping, db_type, user, password, host, port, database):
#     try:
#         df = read_file(file_path)
#         missing_cols = [col for col in column_mapping.keys() if col not in df.columns]
#         if missing_cols:
#             raise ValueError(f"Colonnes manquantes dans le fichier : {missing_cols}")
        
#         df.rename(columns=column_mapping, inplace=True)
        
#         engine = get_db_engine(db_type, user, password, host, port, database)
        
#         with engine.begin() as conn:  # Utilisation de transaction automatique
#             df.to_sql(table_name, con=conn, if_exists='append', index=False, method='multi')
        
#         print("Importation réussie !")
#     except Exception as e:
#         print(f"Erreur lors de l'importation : {e}")

# if __name__ == "__main__":
#     file_path = "request_citizen.csv"
#     table_name = "REQUEST"

#     column_mapping = {
#         "ID_citizen": "ID",
#         "ENROLMENTDATE_citizen": "ENROLMENTDATE",
#         "REGISTRATIONNUMBER_citizen": "REGISTRATIONNUMBER",
#         "IDPI_citizen": "IDPI",
#         "CARDTYPE_citizen": "CARDTYPE",
#         "REQUESTTYPE_citizen": "REQUESTTYPE",
#         "CATEGORY_citizen": "CATEGORY",
#         "PREVIOUSREQUESTIDKIT_citizen": "PREVIOUSREQUESTIDKIT",
#         "PREVIOUSDOCUMENTNUMBER_citizen": "PREVIOUSDOCUMENTNUMBER",
#         "PREVIOUSIDENTITYID_citizen": "PREVIOUSIDENTITYID",
#         "IDDEPOSITCENTER_citizen": "IDDEPOSITCENTER",
#         "NUMBEROFMAILINCLOSURESLIP_citizen": "NUMBEROFMAILINCLOSURESLIP",
#         "RECEIVEDAMOUNT_citizen": "RECEIVEDAMOUNT",
#         "LEFTAMOUNT_citizen": "LEFTAMOUNT",
#         "COMMENTS_citizen": "COMMENTS",
#         "CREATIONDATE_citizen": "CREATIONDATE",
#         "CREATOR_citizen": "CREATOR",
#         "MODIFICATIONDATE_citizen": "MODIFICATIONDATE",
#         "MODIFIER_citizen": "MODIFIER",
#         "REQUESTIDKIT_citizen": "REQUESTIDKIT",
#         "SYNTHESIS_FILENAME_citizen": "SYNTHESIS_FILENAME",
#         "PURGEDEXPORTEDFILES_citizen": "PURGEDEXPORTEDFILES",
#         "PURGEDPDFFILES_citizen": "PURGEDPDFFILES"
#     }

#     db_config = {
#         "db_type": "postgres", 
#         "user": "postgres",
#         "password": "123456",
#         "host": "localhost",
#         "port": "5432",
#         "database": "verify"
#     }

#     import_file_to_db(file_path, table_name, column_mapping, **db_config)




import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import os

def get_db_engine(db_type, user, password, host, port, database):
    if db_type == "mysql":
        return create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    elif db_type == "postgresql" or db_type == "postgres":  # Correction ici
        return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    elif db_type == "oracle":
        return create_engine(f"oracle+cx_oracle://{user}:{password}@{host}:{port}/{database}")
    elif db_type == "sqlite":
        return create_engine(f"sqlite:///{database}")
    else:
        raise ValueError(f"Base de données non supportée : {db_type}")

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
        
        with engine.begin() as conn:  # Utilisation de transaction automatique
            df.to_sql(table_name, con=conn, if_exists='append', index=False, method='multi')
        
        print("Importation réussie !")
    except Exception as e:
        print(f"Erreur lors de l'importation : {e}")

if __name__ == "__main__":
    file_path = "request_citizen.csv"
    table_name = "requeste"

    column_mapping = {
        "ID_citizen": "id",
        "ENROLMENTDATE_citizen": "enrolmentdate",
        "REGISTRATIONNUMBER_citizen": "registrationnumber",
        "IDPI_citizen": "idpi",
        "CARDTYPE_citizen": "cardtype",
        "REQUESTTYPE_citizen": "requesttype",
        "CATEGORY_citizen": "category",
        "PREVIOUSREQUESTIDKIT_citizen": "previousrequestidkit",
        "PREVIOUSDOCUMENTNUMBER_citizen": "previousdocumentnumber",
        "PREVIOUSIDENTITYID_citizen": "previousidentityid",
        "IDDEPOSITCENTER_citizen": "iddepositcenter",
        "NUMBEROFMAILINCLOSURESLIP_citizen": "numberofmailinclosureslip",
        "RECEIVEDAMOUNT_citizen": "receivedamount",
        "LEFTAMOUNT_citizen": "leftamount",
        "COMMENTS_citizen": "comments",
        "CREATIONDATE_citizen": "creationdate",
        "CREATOR_citizen": "creator",
        "MODIFICATIONDATE_citizen": "modificationdate",
        "MODIFIER_citizen": "modifier",
        "REQUESTIDKIT_citizen": "requestidkit",
        "SYNTHESIS_FILENAME_citizen": "synthesis_filename",
        "PURGEDEXPORTEDFILES_citizen": "purgedexportedfiles",
        "PURGEDPDFFILES_citizen": "purgedpdffiles"
    }


    db_config = {
        "db_type": "postgres",  
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432",
        "database": "verify"
    }

    import_file_to_db(file_path, table_name, column_mapping, **db_config)
