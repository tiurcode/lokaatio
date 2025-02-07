import sqlite3  # SQLite-tietokantakirjasto
import osmnx as ox  # Kirjasto OpenStreetMap (OSM) -verkostojen käsittelyyn
import networkx as nx  # Kirjasto analyysiin, jota käytetään OSM-verkoston reititykseen
import pandas as pd  # Kirjasto tietojen käsittelyyn DataFrame-muodossa
from faker import Faker  # Kirjasto satunnaisen datan generointiin
from datetime import datetime, timedelta  # Ajanhallintaan liittyvät luokat
import random  # Satunnaislukujen generointi

# Yhdistetään tietokantaan lokaatiot.db (tai luodaan uusi tietokanta jos sitä ei ole olemassa)
conn = sqlite3.connect('lokaatiot.db')
cursor = conn.cursor()

# Luodaan taulu, jos se ei ole jo olemassa
cursor.execute('''
CREATE TABLE IF NOT EXISTS lokaatiot (
    id INTEGER PRIMARY KEY, 
    laite_id TEXT NOT NULL, 
    timestamp TEXT NOT NULL, 
    lat REAL NOT NULL, 
    lon REAL NOT NULL
)
''')

# Generoidaan satunnaista dataa
fake = Faker('fi_FI')  # Käytetään Faker-kirjastoa suomenkielisen datan generointiin

# Haetaan katuverkosto OSM:stä
place_name = "Tampere, Finland"
graph = ox.graph_from_place(place_name, network_type='drive')  # Haetaan katuverkosto ajoneuvoille

# Funktio reitin lisäämiseksi tietokantaan
def add_route_to_db(laite_id, start_time, rows_per_device=None, days_of_data=None):
    # Valitaan satunnaiset alku- ja loppupisteet verkostosta
    nodes = list(graph.nodes)  # Haetaan kaikki verkoston solmut

    total_rows = 0
    current_time = start_time

    while (rows_per_device is None or total_rows < rows_per_device) and (days_of_data is None or current_time < start_time + timedelta(days=days_of_data)):
        orig_node = random.choice(nodes)  # Satunnainen lähtöpiste
        dest_node = random.choice(nodes)  # Satunnainen määränpää

        try:
            # Lasketaan lyhin reitti alku- ja loppupisteen välille
            route = nx.shortest_path(graph, orig_node, dest_node, weight='length')
        except nx.NetworkXNoPath:
            # Jos reittiä ei löydy, tulostetaan virheilmoitus ja jatketaan seuraavaan iterointiin
            print("Reittiä ei löydettävissä")
            continue

        # Hankitaan reitin koordinaatit
        route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]

        # Luodaan aikaleimat reitin pisteille 5 sekunnin välein
        time_intervals = [current_time + timedelta(seconds=5 * i) for i in range(len(route_coords))]

        # Lisätään reitti tietokantaan
        for coords, timestamp in zip(route_coords, time_intervals):
            cursor.execute('''
            INSERT INTO lokaatiot (laite_id, timestamp, lat, lon)
            VALUES (?, ?, ?, ?)
            ''', (laite_id, timestamp.strftime('%Y-%m-%d %H:%M:%S'), coords[0], coords[1]))  # Lisää rivi tietokantaan
            total_rows += 1
            if rows_per_device is not None and total_rows >= rows_per_device:
                break
        
        current_time = time_intervals[-1] + timedelta(seconds=5)  # Päivitetään nykyinen aika

    conn.commit()  # Tallennetaan muutokset tietokantaan
    print(f"Lisätty {total_rows} riviä laitteelle: {laite_id}")  # Tulostetaan ilmoitus onnistuneesta lisäyksestä

# Aloitusaika datalle
start_time = datetime.now()  # Nykyinen aika

# Määritellään parametrien arvot
rows_per_device = 100  # Esimerkiksi 1000 riviä per laite
days_of_data = 1  # Esimerkiksi 1 päivän data

# Lisätään reitit kahdelle laitteelle
add_route_to_db('a', start_time, rows_per_device, days_of_data)  # Lisää reitti laitteelle 'a'
add_route_to_db('b', start_time, rows_per_device, days_of_data)  # Lisää reitti laitteelle 'b'

# Suljetaan yhteys
conn.close()  # Suljetaan tietokantayhteys
