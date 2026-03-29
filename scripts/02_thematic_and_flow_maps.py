import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import folium
from shapely.geometry import Point, LineString

# ==========================================
# SETUP: Re-loading Part 0 data for continuity
# ==========================================
print("Loading base data...")
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url).rename(columns={'NAME': 'name', 'ISO_A3': 'iso_a3', 'POP_EST': 'pop_est'})
world = world[(world.name != "Antarctica")]
world['pop_2023'] = pd.to_numeric(world['pop_est'], errors='coerce').fillna(1) # Avoid div by zero

# Mock Emissions Data
np.random.seed(42)
world['co2_emissions_mt'] = np.random.uniform(10, 5000, size=len(world)) 


# ==========================================
# PART 2: CHOROPLETH MAP AND PITFALLS
# Requirement: Normalized data, 2 classification methods compared
# ==========================================
print("\n--- Executing Part 2: Choropleths ---")

# 1. Normalize the Data (Creating a Rate/Ratio as required)
# CO2 Emissions per Capita (Metric Tons per person)
world['co2_per_capita'] = (world['co2_emissions_mt'] * 1000000) / world['pop_2023']

# 2. Compare Classifications
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Normalized Variable: CO2 Emissions Per Capita", fontsize=16)

# Map 2A: Quantiles (Distributes same number of countries into each color bucket)
world.plot(column='co2_per_capita', ax=axes[0], scheme='Quantiles', k=5, cmap='Purples',
           legend=True, legend_kwds={'loc': 'lower left', 'fmt': "{:.2f}"})
axes[0].set_title("Classification: Quantiles (Highlights Relative Rank)", fontsize=12)
axes[0].set_axis_off()

# Map 2B: Equal Interval (Divides the data range into equal-sized mathematical buckets)
world.plot(column='co2_per_capita', ax=axes[1], scheme='EqualInterval', k=5, cmap='Purples',
           legend=True, legend_kwds={'loc': 'lower left', 'fmt': "{:.2f}"})
axes[1].set_title("Classification: Equal Interval (Highlights Outliers/Skew)", fontsize=12)
axes[1].set_axis_off()

plt.tight_layout()
plt.savefig("Task2_Choropleth_Comparison.png", dpi=300)
print("Saved Task2_Choropleth_Comparison.png")
plt.close()


# ==========================================
# MOCKING POINT & FLOW DATA FOR PARTS 3 & 4
# ==========================================
# 15 Major Global Airports
airport_data = {
    'code': ['ATL', 'PEK', 'DXB', 'LAX', 'HND', 'ORD', 'LHR', 'PVG', 'CDG', 'DFW', 'AMS', 'FRA', 'IST', 'CAN', 'JFK'],
    'name': ['Atlanta', 'Beijing', 'Dubai', 'Los Angeles', 'Tokyo', 'Chicago', 'London', 'Shanghai', 'Paris', 'Dallas', 'Amsterdam', 'Frankfurt', 'Istanbul', 'Guangzhou', 'New York'],
    'lat': [33.64, 40.08, 25.25, 33.94, 35.55, 41.98, 51.47, 31.14, 49.00, 32.89, 52.30, 50.03, 41.27, 23.39, 40.64],
    'lon': [-84.42, 116.58, 55.36, -118.40, 139.77, -87.90, -0.45, 121.80, 2.54, -97.04, 4.76, 8.57, 28.72, 113.29, -73.77],
    'traffic_millions': [110, 100, 89, 88, 87, 83, 80, 76, 76, 75, 71, 70, 68, 65, 62]
}
df_airports = pd.DataFrame(airport_data)
df_airports['geometry'] = [Point(xy) for xy in zip(df_airports.lon, df_airports.lat)]
gdf_airports = gpd.GeoDataFrame(df_airports, geometry='geometry', crs="EPSG:4326")

# Mock Flight Routes (Flows) between these hubs
routes = [
    ('JFK', 'LHR', 3.0), ('JFK', 'CDG', 2.0), ('LHR', 'DXB', 4.5), ('DXB', 'HND', 2.5),
    ('ATL', 'LAX', 5.0), ('LAX', 'HND', 3.5), ('PEK', 'PVG', 6.0), ('FRA', 'JFK', 2.2),
    ('AMS', 'DXB', 1.8), ('IST', 'FRA', 2.0), ('ORD', 'DFW', 4.0), ('DFW', 'LAX', 3.8),
    ('HND', 'PEK', 3.2), ('LHR', 'FRA', 4.1), ('CDG', 'AMS', 1.5)
]
df_flows = pd.DataFrame(routes, columns=['origin', 'dest', 'pax_millions'])


# ==========================================
# PART 3: PROPORTIONAL SYMBOL MAP
# Requirement: Scale by area, reduce overlap, 1 static, 1 interactive
# ==========================================
print("\n--- Executing Part 3: Proportional Symbols ---")

# 3A. STATIC MAP (Matplotlib)
fig, ax = plt.subplots(1, 1, figsize=(12, 6))
world.plot(ax=ax, color='lightgrey', edgecolor='white')

# Scale by AREA (s parameter in scatter represents area, not radius)
# Using alpha=0.6 to reduce overlap visual clutter
scatter = ax.scatter(gdf_airports.lon, gdf_airports.lat, 
                     s=gdf_airports['traffic_millions']*5, # Scaling factor for visibility
                     c='red', alpha=0.6, edgecolors='darkred')

ax.set_title("Global Airport Traffic (Proportional Symbols by Area)", fontsize=14)
ax.set_axis_off()
plt.savefig("Task3_Proportional_Symbols_Static.png", dpi=300)
print("Saved Task3_Proportional_Symbols_Static.png")
plt.close()

# ==========================================
# PART 3B: INTERACTIVE MAP (Folium) - EXTRA CREDIT EDITION
# ==========================================
print("\nGenerating Extra Credit Interactive Map...")

# Center map globally with a default basemap
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# EXTRA CREDIT 1: Compare multiple basemaps
folium.TileLayer('OpenStreetMap', name='Standard Map').add_to(m)
folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)

for idx, row in gdf_airports.iterrows():
    radius_scaled = np.sqrt(row['traffic_millions']) * 1.5 
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=radius_scaled,
        # EXTRA CREDIT 2: Add hover tooltips (HTML formatted)
        tooltip=f"<b>{row['name']} ({row['code']})</b><br>{row['traffic_millions']}M Passengers",
        color="crimson",
        fill=True,
        fill_color="crimson",
        fill_opacity=0.6 
    ).add_to(m)

# Add the interactive menu to toggle the basemaps
folium.LayerControl().add_to(m)

m.save("Task3_Proportional_Symbols_Interactive_Bonus.html")
print("Saved Task3_Proportional_Symbols_Interactive_Bonus.html with tooltips and basemap toggles!")

# ==========================================
# PART 4: FLOW MAP / MOVEMENT ANALYSIS
# Requirement: Encode width, filter clutter, NetworkX stats
# ==========================================
print("\n--- Executing Part 4: Flow Map & Network Analysis ---")

# 4A. Network Analysis using NetworkX
G = nx.DiGraph()
for _, row in df_flows.iterrows():
    G.add_edge(row['origin'], row['dest'], weight=row['pax_millions'])

# Calculate Network Statistics
in_degree = dict(G.in_degree(weight='weight'))
out_degree = dict(G.out_degree(weight='weight'))
degree_centrality = nx.degree_centrality(G) # How well-connected a hub is

# Create Summary Table
df_network_stats = pd.DataFrame({
    'Inflow_Pax_M': pd.Series(in_degree),
    'Outflow_Pax_M': pd.Series(out_degree),
    'Centrality_Score': pd.Series(degree_centrality)
}).fillna(0).sort_values(by='Inflow_Pax_M', ascending=False)

print("\n--- Network Summary Table ---")
print(df_network_stats.head())

# 4B. Generate Flow Map Geometries
flow_lines = []
for _, row in df_flows.iterrows():
    orig = df_airports[df_airports['code'] == row['origin']].iloc[0]
    dest = df_airports[df_airports['code'] == row['dest']].iloc[0]
    line = LineString([(orig['lon'], orig['lat']), (dest['lon'], dest['lat'])])
    flow_lines.append({'geometry': line, 'pax_millions': row['pax_millions']})

gdf_flows = gpd.GeoDataFrame(flow_lines, crs="EPSG:4326")

# 4C. Plot Flow Map
fig, ax = plt.subplots(1, 1, figsize=(14, 7))
world.to_crs("+proj=robin").plot(ax=ax, color='lightgrey', edgecolor='white')

# Reproject flows to match basemap (Robinson)
gdf_flows_proj = gdf_flows.to_crs("+proj=robin")

# Encode magnitude using line width (Requirement)
for _, row in gdf_flows_proj.iterrows():
    x, y = row['geometry'].xy
    ax.plot(x, y, color='blue', linewidth=row['pax_millions'], alpha=0.5, solid_capstyle='round')

ax.set_title("Global Airline Corridors: Top Routes by Passenger Volume", fontsize=16)
ax.text(0.5, 0.02, "Line width indicates passenger magnitude | Computed via NetworkX", 
         ha='center', transform=ax.transAxes, fontsize=10, style='italic')
ax.set_axis_off()

plt.tight_layout()
plt.savefig("Task4_Flow_Map.png", dpi=300)
print("Saved Task4_Flow_Map.png")
plt.close()

print("\nAll map generation scripts for Parts 2, 3, and 4 completed successfully!")