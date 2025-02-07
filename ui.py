import sqlite3
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

# Yhdistetään tietokantaan ja haetaan data
conn = sqlite3.connect('lokaatiot.db')
query = "SELECT laite_id, timestamp, lat, lon FROM lokaatiot"
df = pd.read_sql_query(query, conn)
conn.close()

# Muunnetaan aikasarake datetime-objekteiksi
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Muunnetaan aikaleimat merkkijonoiksi
df['timestamp_str'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Streamlit käyttöliittymä
st.title("Reitin seuranta")

# Määritellään värit eri laite-ID:ille
colors = {
    'a': 'red',
    'b': 'blue',
    # Lisää muita laite-ID:tä ja värejä tarpeen mukaan
}

# Funktio luomaan kartan
def create_base_map():
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13)
    return m

# Funktio päivittämään karttaa
def update_map(m, df, start_time, end_time, selected_device):
    if selected_device != 'kaikki':
        df = df[df['laite_id'] == selected_device]
        
    for laite_id, group in df.groupby('laite_id'):
        color = colors.get(laite_id, 'black')  # Oletusvärinä musta, jos laite_id:lle ei löydy väriä
        group = group[(group['timestamp'] >= start_time) & (group['timestamp'] <= end_time)]
        folium.PolyLine(group[['lat', 'lon']].values, color=color, weight=2.5, opacity=1).add_to(m)
        for _, row in group.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=3,  # Pienempi radius tekee merkistä pienemmän pisteen
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"Device: {row['laite_id']}<br>Time: {row['timestamp']}"
            ).add_to(m)
    return m

# Luodaan paikkamerkki kartalle
map_placeholder = st.empty()

# Valitaan ajanjakso select sliderilla
time_range = df['timestamp_str'].unique()
start_time_str, end_time_str = st.select_slider(
    "Valitse ajanjakso",
    options=time_range,
    value=(time_range.min(), time_range.max())
)

# Muunnetaan valinnat datetime-objekteiksi
start_time = pd.to_datetime(start_time_str)
end_time = pd.to_datetime(end_time_str)

# Valitaan laite-ID
device_options = ['kaikki'] + df['laite_id'].unique().tolist()
selected_device = st.selectbox("Valitse laite-ID", device_options)

# Päivitetään kartta valitulla ajanjaksolla ja laite-ID:llä
base_map = create_base_map()
updated_map = update_map(base_map, df, start_time, end_time, selected_device)
with map_placeholder:
    folium_static(updated_map, width=1600, height=1000)
