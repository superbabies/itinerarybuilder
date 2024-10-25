import os
import mysql.connector
from dotenv import load_dotenv


def create_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_IP"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="itinerary_builder",  # optional
        port=3306  # default MySQL port
    )

    if connection.is_connected():
        print(f'Connected as id {connection.connection_id}')
    return connection