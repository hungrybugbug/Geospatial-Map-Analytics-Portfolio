import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from shapely.geometry import Point, Polygon

# ==========================================
# SETUP: Re-loading Part 0 data for basemaps
# ==========================================
print("Loading base data...")
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url).rename(columns={'NAME': 'name', 'ISO_A3': 'iso_a3', 'POP_EST': 'pop_est'})
world = world[(world.name != "Antarctica")]
world['pop_2023'] = pd.to_numeric(world['pop_est'], errors='coerce').fillna(1)

# FIX: Recalculate area and pop_density for Part 7
world['area_sqkm'] = world.to_crs('+proj=cea').geometry.area / 10**6
world['pop_density'] = world['pop_2023'] / world['area_sqkm']

# ==========================================
# PART 5: CONTINUOUS FIELD MAPPING
# Requirement: Point map + Interpolated contour map (SciPy)
# ==========================================
print("\n--- Executing Part 5: Continuous Fields ---")

# 1. Generate Mock Weather Stations (e.g., Temperature in a bounded region)
np.random.seed(42)
lons = np.random.uniform(-10, 30, 100) # Longitudes (Europe region roughly)
lats = np.random.uniform(35, 60, 100)  # Latitudes
# Temperature gets colder as latitude increases (plus some randomness)
temps = 30 - (lats - 35) * 0.8 + np.random.normal(0, 3, 100) 

# 2. Setup the Interpolation Grid
grid_x, grid_y = np.mgrid[-15:35:200j, 30:65:200j]

# 3. Perform Grid Interpolation (Cubic)
grid_z = griddata((lons, lats), temps, (grid_x, grid_y), method='cubic')

# 4. Plot Point Map vs Contour Map
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Continuous Spatial Field: Regional Temperature Estimation", fontsize=16)

# Map 5A: Raw Point Measurements
world.plot(ax=axes[0], color='whitesmoke', edgecolor='lightgray')
scatter = axes[0].scatter(lons, lats, c=temps, cmap='coolwarm', edgecolor='k')
axes[0].set_xlim(-15, 35); axes[0].set_ylim(30, 65)
axes[0].set_title("Raw Data: Weather Station Points", fontsize=12)
axes[0].set_axis_off()

# Map 5B: Interpolated Surface (Contour)
world.plot(ax=axes[1], color='whitesmoke', edgecolor='lightgray')
contour = axes[1].contourf(grid_x, grid_y, grid_z, levels=15, cmap='coolwarm', alpha=0.7)
axes[1].scatter(lons, lats, c='black', s=5) # Show original points tiny
axes[1].set_xlim(-15, 35); axes[1].set_ylim(30, 65)
axes[1].set_title("Interpolated Surface: Isopleth / Contour Map", fontsize=12)
axes[1].set_axis_off()

# Add Colorbar
cbar = fig.colorbar(contour, ax=axes.ravel().tolist(), shrink=0.8)
cbar.set_label('Temperature (°C)')

plt.savefig("Task5_Continuous_Field.png", dpi=300)
print("Saved Task5_Continuous_Field.png")
plt.close()


# ==========================================
# PART 6: CARTOGRAM / AREA CORRECTION
# Requirement: Standard map vs Area-corrected representation
# ==========================================
print("\n--- Executing Part 6: Area Correction (Pseudo-Cartogram) ---")

# Convert to Web Mercator to calculate centroids accurately for plotting
world_proj = world.to_crs("EPSG:3857")
world_proj['centroid'] = world_proj.geometry.centroid

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("The 'Size vs Data' Effect: Global Population", fontsize=16)

# Map 6A: Standard Geographic Map (Misleading for absolute counts)
world_proj.plot(column='pop_2023', ax=axes[0], cmap='Blues', scheme='quantiles', k=5)
axes[0].set_title("Standard Map: Area dominates visual weight", fontsize=12)
axes[0].set_axis_off()
axes[0].text(0.02, 0.02, "Russia & Canada appear massive, implying high data values.", 
             transform=axes[0].transAxes, fontsize=10)

# Map 6B: Dorling Cartogram (Proportional Centroid Bubbles)
world_proj.plot(ax=axes[1], color='whitesmoke', edgecolor='lightgrey') # Background
x = world_proj['centroid'].x
y = world_proj['centroid'].y
sizes = world_proj['pop_2023'] / 200000 # Scale down population for visual radii

axes[1].scatter(x, y, s=sizes, color='dodgerblue', alpha=0.7, edgecolor='navy')
axes[1].set_title("Alternative: Dorling Cartogram (Area = Population)", fontsize=12)
axes[1].set_axis_off()
axes[1].text(0.02, 0.02, "China & India dominate, accurately reflecting the data.", 
             transform=axes[1].transAxes, fontsize=10)

plt.tight_layout()
plt.savefig("Task6_Area_Correction.png", dpi=300)
print("Saved Task6_Area_Correction.png")
plt.close()


# ==========================================
# PART 7: CASE-BASED MAP DESIGN CHALLENGE
# Requirement: Implement 3 scenarios (Health, Urban, Climate)
# ==========================================
print("\n--- Executing Part 7: Map Design Scenarios ---")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Part 7: Case-Based Map Design Scenarios", fontsize=16, y=1.05)

# SCENARIO A: Public Health (Disease Burden & Clustering)
cases_lon = np.random.uniform(-10, 10, 500)
cases_lat = np.random.uniform(40, 50, 500)
world.plot(ax=axes[0], color='whitesmoke', edgecolor='lightgray')
hb = axes[0].hexbin(cases_lon, cases_lat, gridsize=15, cmap='Reds', mincnt=1, alpha=0.8)
axes[0].set_xlim(-15, 15); axes[0].set_ylim(35, 55)
axes[0].set_title("Scenario A: Public Health\n(Hexbin / Density Map)", fontsize=12)
axes[0].set_axis_off()

# SCENARIO B: Urban Services (Accessibility)
hospitals = gpd.GeoDataFrame(geometry=[Point(2, 48), Point(5, 45), Point(-2, 43)], crs="EPSG:4326")
hospitals_proj = hospitals.to_crs("+proj=cea") 
service_areas = hospitals_proj.geometry.buffer(200000) # 200km service radius
service_areas_latlon = service_areas.to_crs("EPSG:4326")

world.plot(ax=axes[1], color='whitesmoke', edgecolor='lightgray')
service_areas_latlon.plot(ax=axes[1], color='blue', alpha=0.3, edgecolor='blue')
hospitals.plot(ax=axes[1], color='red', marker='+', markersize=100)
axes[1].set_xlim(-10, 15); axes[1].set_ylim(35, 55)
axes[1].set_title("Scenario B: Urban Services\n(Point Map + Service Buffers)", fontsize=12)
axes[1].set_axis_off()

# SCENARIO C: Climate Risk (Flood Hazard + Population)
flood_poly = Polygon([(-5, 40), (0, 40), (5, 45), (0, 48), (-5, 45)])
flood_gdf = gpd.GeoDataFrame(geometry=[flood_poly], crs="EPSG:4326")

world.plot(column='pop_density', ax=axes[2], cmap='Greys', scheme='quantiles', k=4) 
flood_gdf.plot(ax=axes[2], color='cyan', alpha=0.5, hatch='///', edgecolor='blue') 
axes[2].set_xlim(-15, 15); axes[2].set_ylim(35, 55)
axes[2].set_title("Scenario C: Climate Risk\n(Overlay: Hazard + Vulnerability)", fontsize=12)
axes[2].set_axis_off()

plt.tight_layout()
plt.savefig("Task7_Scenarios.png", dpi=300)
print("Saved Task7_Scenarios.png")
plt.show()

print("\nAll map generation scripts completed! You now have all the visual assets required.")