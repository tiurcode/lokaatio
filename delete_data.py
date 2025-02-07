import os
import sqlite3

# Tietokantatiedoston nimi
db_file = 'lokaatiot.db'

# Sulje SQLite-yhteys, jos se on auki
def close_db_connection():
    try:
        conn = sqlite3.connect(db_file)
        conn.close()
        print(f"SQLite-yhteys tietokantaan '{db_file}' on suljettu.")
    except Exception as e:
        print(f"Virhe suljettaessa tietokantayhteyttä: {e}")

# Poistetaan tietokanta, jos se on olemassa
def delete_database():
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Tietokanta '{db_file}' on poistettu.")
    else:
        print(f"Tiedostoa '{db_file}' ei löydy.")

# Sulje mahdolliset auki olevat yhteydet ja poista tietokanta
close_db_connection()
delete_database()
