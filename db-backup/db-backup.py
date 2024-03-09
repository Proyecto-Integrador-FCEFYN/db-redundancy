import argparse, socket, sys, os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from time import sleep
import logging

# Configuración básica del registro
logging.basicConfig(filename='/home/dbbackupuser/db_backup.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def create_connection_uri(ip, port, user, password):
    """
    Crea y devuelve la URI de conexión para MongoDB.

    Args:
    - ip (str): Dirección IP del host de la base de datos.
    - port (int): Puerto de la base de datos.
    - user (str): Nombre de usuario para la autenticación (opcional).
    - password (str): Contraseña para la autenticación (opcional).

    Returns:
    str: URI de conexión de MongoDB.
    """
    if user and password:
        return f"mongodb://{user}:{password}@{ip}:{port}"
    else:
        return f"mongodb://{ip}:{port}"


def test_connection_to_db(database_host, database_port):
    """
    Prueba la conexión a la base de datos.

    Args:
    - database_host (str): Dirección IP o nombre de host de la base de datos.
    - database_port (int): Puerto de la base de datos.

    Returns:
    bool: True si la conexión es exitosa, False de lo contrario.
    """
    try:
        s = socket.create_connection((database_host, database_port), 5)
        s.close()
        return True
    except:
        return False


def collection_exists(db, collection_name):
    """
    Verifica si una colección existe en la base de datos.

    Args:
    - db (pymongo.database.Database): Objeto de base de datos de pymongo.
    - collection_name (str): Nombre de la colección a verificar.

    Returns:
    bool: True si la colección existe, False de lo contrario.
    """
    collections = db.collection_names()
    return collection_name in collections


def backup_mongodb(backup_ip, backup_port, backup_user, backup_password, backup_database_name,
                   default_ip, default_port, default_user, default_password, default_database_name,
                   from_default_to_backup=True):
    """
    Realiza la operación de respaldo de MongoDB.

    Args:
    - backup_ip (str): Dirección IP del host de la base de datos de respaldo.
    - backup_port (int): Puerto de la base de datos de respaldo.
    - backup_user (str): Nombre de usuario para la autenticación de la base de datos de respaldo (opcional).
    - backup_password (str): Contraseña para la autenticación de la base de datos de respaldo (opcional).
    - backup_database_name (str): Nombre de la base de datos de respaldo.
    - default_ip (str): Dirección IP del host de la base de datos por defecto.
    - default_port (int): Puerto de la base de datos por defecto.
    - default_user (str): Nombre de usuario para la autenticación de la base de datos por defecto (opcional).
    - default_password (str): Contraseña para la autenticación de la base de datos por defecto (opcional).
    - default_database_name (str): Nombre de la base de datos por defecto.
    - from_default_to_backup (bool): Indica la dirección del respaldo. True si es desde la base de datos default a la de backup, False de lo contrario.
    """
    if from_default_to_backup:
        backup_uri = create_connection_uri(backup_ip, backup_port, backup_user, backup_password)
        default_uri = create_connection_uri(default_ip, default_port, default_user, default_password)
        backup_client = MongoClient(backup_uri)
        backup_db = backup_client[backup_database_name]

        default_client = MongoClient(default_uri)
        default_db = default_client[default_database_name]
    else:
        backup_uri = create_connection_uri(default_ip, default_port, default_user, default_password)
        default_uri = create_connection_uri(backup_ip, backup_port, backup_user, backup_password)
        backup_client = MongoClient(backup_uri)
        backup_db = backup_client[default_database_name]

        default_client = MongoClient(default_uri)
        default_db = default_client[backup_database_name]

    collections = backup_db.collection_names()
    collections = [coll for coll in collections if not coll.startswith("django_") and coll != "__schema__"]

    for collection_name in collections:
        collection_data = backup_db[collection_name].find()

        if not collection_exists(default_db, collection_name):
            default_db.create_collection(collection_name)

        for document in collection_data:
            document_id = document['_id']

            existing_document = default_db[collection_name].find_one({'_id': document_id})

            try:
                if existing_document:
                    default_db[collection_name].replace_one({'_id': document_id}, document)
                    logging.info(f"Documento actualizado en {collection_name}")
                else:
                    default_db[collection_name].insert_one(document)
                    logging.info(f"Documento insertado en {collection_name}")
            except DuplicateKeyError:
                logging.info(f"No se pudo insertar/actualizar documento en {collection_name} debido a una clave duplicada no detectada")
                continue


    collections_default = default_db.collection_names()
    collections_default = [coll for coll in collections_default if not coll.startswith("django_") and coll != "__schema__"]

    for collection_name in collections_default:
        collection_data = default_db[collection_name].find()

        for document in collection_data:
            document_id = document['_id']

            existing_document = backup_db[collection_name].find_one({'_id': document_id})

            if not existing_document:
                default_db[collection_name].delete_one({"_id": document_id})
                logging.info(f"Documento {document_id} eliminado de {collection_name}.")

    logging.info("Backup completado con éxito.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script para realizar backup de base de datos MongoDB')
    parser.add_argument('--backup_ip', required=True, help='IP de la base de datos de backup')
    parser.add_argument('--backup_port', required=True, help='Puerto de la base de datos de backup')
    parser.add_argument('--backup_user', default=None, help='Usuario de la base de datos de backup')
    parser.add_argument('--backup_password', default=None, help='Contraseña de la base de datos de backup')
    parser.add_argument('--backup_database_name', required=True, help='Nombre de la base de datos de backup')

    parser.add_argument('--default_ip', required=True, help='IP de la base de datos default')
    parser.add_argument('--default_port', required=True, help='Puerto de la base de datos default')
    parser.add_argument('--default_user', default=None, help='Usuario de la base de datos default')
    parser.add_argument('--default_password', default=None, help='Contraseña de la base de datos default')
    parser.add_argument('--default_database_name', required=True, help='Nombre de la base de datos default')

    parser.add_argument('--polling_secs', default=30, type=int, help='Cantidad de segundos de polling entre actualizaciones')

    args = parser.parse_args()


    available = True
    data_recovered = True
    while True:
        try:
            available = test_connection_to_db(args.default_ip, args.default_port)
            if available and data_recovered:
                logging.info('Base DEFAULT conectada.')
                backup_mongodb(args.default_ip, args.default_port, args.default_user, args.default_password, args.default_database_name,
                               args.backup_ip, args.backup_port, args.backup_user, args.backup_password, args.backup_database_name, from_default_to_backup=True)
                sleep(args.polling_secs)
            else:
                while not available:
                    logging.error('Error en base DEFAULT. Esperando a que vuelva...')
                    sleep(5)
                    available = test_connection_to_db(args.default_ip, args.default_port)
                    data_recovered = False

                logging.info('Retornó base DEFAULT. Recuperando datos guardados en backup.')
                backup_mongodb(args.default_ip, args.default_port, args.default_user, args.default_password, args.default_database_name,
                               args.backup_ip, args.backup_port, args.backup_user, args.backup_password, args.backup_database_name, from_default_to_backup=False)
                data_recovered = True
                logging.info('Datos recuperados.')
                sleep(args.polling_secs)
        except Exception as e:
            logging.error('Se produjo un error: ' + str(e))
