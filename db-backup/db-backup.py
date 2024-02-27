##
#
#
# python3 backup-periodico-3.py --remote_ip 150.136.250.71 --remote_port 27017 --remote_user roberto --remote_password sanchez --remote_database_name djongo --local_ip localhost --local_port 27017  --local_database_name djongo2
##

import argparse, socket, sys, os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from time import sleep

# Redirigir stdout a un archivo específico
log_file = '/home/dbbackupuser/db_backup.log'

# Verificar si el archivo de registro existe, si no, crearlo
if not os.path.exists(log_file):
    open(log_file, 'a').close()

# Redirigir stdout a un archivo específico
sys.stdout = open(log_file, 'a')

def create_connection_uri(ip, port, user, password):
    if user and password:
        return f"mongodb://{user}:{password}@{ip}:{port}"
    else:
        return f"mongodb://{ip}:{port}"


def test_connection_to_db(database_host, database_port):
    try:
        s = socket.create_connection((database_host, database_port), 5)
        s.close()
        return True
    except:
        return False


def collection_exists(db, collection_name):
    collections = db.collection_names()
    return collection_name in collections


def backup_mongodb(remote_ip, remote_port, remote_user, remote_password, remote_database_name,
                   local_ip, local_port, local_user, local_password, local_database_name,
                   from_remote_to_local=True):
    if from_remote_to_local:
        remote_uri = create_connection_uri(remote_ip, remote_port, remote_user, remote_password)
        local_uri = create_connection_uri(local_ip, local_port, local_user, local_password)
        remote_client = MongoClient(remote_uri)
        remote_db = remote_client[remote_database_name]

        local_client = MongoClient(local_uri)
        local_db = local_client[local_database_name]
    else:
        remote_uri = create_connection_uri(local_ip, local_port, local_user, local_password)
        local_uri = create_connection_uri(remote_ip, remote_port, remote_user, remote_password)
        remote_client = MongoClient(remote_uri)
        remote_db = remote_client[local_database_name]

        local_client = MongoClient(local_uri)
        local_db = local_client[remote_database_name]

    print("URIS: ", remote_uri , local_uri)

    collections = remote_db.collection_names()
    collections = [coll for coll in collections if not coll.startswith("django_") and coll != "__schema__"]

    for collection_name in collections:
        collection_data = remote_db[collection_name].find()

        if not collection_exists(local_db, collection_name):
            local_db.create_collection(collection_name)

        for document in collection_data:
            document_id = document['_id']

            existing_document = local_db[collection_name].find_one({'_id': document_id})

            try:
                if existing_document:
                    local_db[collection_name].replace_one({'_id': document_id}, document)
                    print(f"Documento actualizado en {collection_name}")
                else:
                    local_db[collection_name].insert_one(document)
                    print(f"Documento insertado en {collection_name}")
            except DuplicateKeyError:
                print(f"No se pudo insertar/actualizar documento en {collection_name} debido a una clave duplicada no detectada")
                continue

    print("Backup completado con éxito.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script para realizar backup de base de datos MongoDB')
    parser.add_argument('--remote_ip', required=True, help='IP de la base de datos remota')
    parser.add_argument('--remote_port', required=True, help='Puerto de la base de datos remota')
    parser.add_argument('--remote_user', default=None, help='Usuario de la base de datos remota')
    parser.add_argument('--remote_password', default=None, help='Contraseña de la base de datos remota')
    parser.add_argument('--remote_database_name', required=True, help='Nombre de la base de datos remota')

    parser.add_argument('--local_ip', required=True, help='IP de la base de datos local')
    parser.add_argument('--local_port', required=True, help='Puerto de la base de datos local')
    parser.add_argument('--local_user', default=None, help='Usuario de la base de datos local')
    parser.add_argument('--local_password', default=None, help='Contraseña de la base de datos local')
    parser.add_argument('--local_database_name', required=True, help='Nombre de la base de datos local')

    parser.add_argument('--polling_secs', default=30, type=int, help='Cantidad de segundos de polling entre actualizaciones')

    args = parser.parse_args()


    available = True
    while True:
        available = test_connection_to_db(args.remote_ip, args.remote_port)
        if available:
            print('Base DEFAULT conectada.')
            try:
                backup_mongodb(args.remote_ip, args.remote_port, args.remote_user, args.remote_password, args.remote_database_name,
                   args.local_ip, args.local_port, args.local_user, args.local_password, args.local_database_name, from_remote_to_local=True)
            except Exception as e:
                print('Error: '+ str(e) )
                print('EXIT')
            sleep(args.polling_secs)
        else:
            while(not available):
                print('Error en base DEFAULT. Esperando a que vuelva...')
                sleep(5)
                available = test_connection_to_db(args.remote_ip, args.remote_port)
            try:
                print('Retornó base DEFAULT. Recuperando datos guardados en backup.')
                backup_mongodb(args.remote_ip, args.remote_port, args.remote_user, args.remote_password, args.remote_database_name,
                   args.local_ip, args.local_port, args.local_user, args.local_password, args.local_database_name, from_remote_to_local=False)
            except Exception as e:
                print('Error: '+ str(e) )
                print('EXIT')


# Backup completado con éxito.
# Base DEFAULT conectada.
# URIS:  mongodb://roberto:sanchez@150.136.250.71:27017 mongodb://localhost:27017
# Documento actualizado en users_timezone
# Documento actualizado en users_timezone
# Documento actualizado en users_timezone
# Documento actualizado en users_timezone
# Documento actualizado en users_category
# Documento actualizado en users_category
# Documento actualizado en users_category
# Documento actualizado en users_category
# Documento actualizado en users_user_category_list
# Documento actualizado en users_user_category_list
# Documento actualizado en events_movementtimezone
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en events_eventsduration
# Documento actualizado en devices_device
# Documento actualizado en devices_device
# Documento actualizado en devices_device
# Documento actualizado en users_visitor
# Documento actualizado en users_visitor
# Documento actualizado en devices_device_category_list
# Documento actualizado en devices_device_category_list
# Documento actualizado en users_user
# Documento actualizado en users_user
# Backup completado con éxito.
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Error en base DEFAULT. Esperando a que vuelva...
# Retornó base DEFAULT. Recuperando datos guardados en backup.
# URIS:  mongodb://localhost:27017 mongodb://roberto:sanchez@150.136.250.71:27017
# Documento actualizado en users_category
# Documento actualizado en users_category
# Documento actualizado en users_category
# Documento actualizado en users_category
# Documento insertado en users_category
# Documento actualizado en users_timezone
# Documento actualizado en users_timezone
# Documento actualizado en users_timezone
# Documento actualizado en users_timezone
# Documento actualizado en devices_device_category_list
# Documento actualizado en devices_device_category_list
# Documento actualizado en devices_device_category_list
# Documento insertado en devices_device_category_list
# Documento insertado en devices_device_category_list
# Documento actualizado en devices_device
# Documento actualizado en devices_device
# Documento actualizado en devices_device
# Documento insertado en devices_device
# Documento actualizado en users_user_category_list
# Documento actualizado en users_user_category_list
# Documento actualizado en users_user
# Documento actualizado en users_user
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en auth_permission
# Documento actualizado en events_movementtimezone
# Documento actualizado en events_eventsduration
# Documento actualizado en users_visitor
# No se pudo insertar/actualizar documento en users_visitor debido a una clave duplicada no detectada
# Documento actualizado en users_visitor
# Backup completado con éxito.
# Base DEFAULT conectada.
