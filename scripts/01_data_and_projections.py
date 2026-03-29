import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# PART 0: DATA ACQUISITION, CLEANING & JOINS
# Requirement Checklist: 4 datasets, 2 joins, 2+ geometry types
# ==========================================
print("Starting Data Acquisition and Preprocessing...")

# 1. POLYGON DATASET (Global Admin Boundaries)
# FIX: GeoPandas 1.0+ removed built-in datasets. We fetch directly from Natural Earth.
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)

# The raw Natural Earth dataset uses uppercase column names. 
# We rename them here so they match the rest of our analysis perfectly.
world = world.rename(columns={'NAME': 'name', 'ISO_A3': 'iso_a3', 'POP_EST': 'pop_est'})

# Clean: Drop Antarctica as it skews visual population density
world = world[(world.name != "Antarctica")] 

# --- REQUIREMENT: PERFORM AT LEAST 2 DATASET JOINS ---
# Simulating a loaded CSV with ISO codes and Population
df_pop = pd.DataFrame({
    'iso_a3': world['iso_a3'].tolist(),
    'pop_2023': world['pop_est'] * 1.05 # Mocking updated population
})
# Perform Join 1
world = world.merge(df_pop, on='iso_a3', how='left')
print("Join 1 Complete: Population data merged to country polygons.")

# Join 2: CO2 Emissions Data
# Simulating a loaded CSV with ISO codes and Emissions (in Megatonnes)
np.random.seed(42)
df_emissions = pd.DataFrame({
    'iso_a3': world['iso_a3'].tolist(),
    'co2_emissions_mt': np.random.uniform(10, 5000, size=len(world)) 
})
# Perform Join 2
world = world.merge(df_emissions, on='iso_a3', how='left')
print("Join 2 Complete: Emissions data merged to country polygons.")

# --- PREPARE DATA FOR PROJECTION CHALLENGE ---
# Calculate Population Density using an equal-area projection (CEA) for accurate sq km
# We fill NaN values with 0 just in case the raw data had missing population estimates
world['pop_2023'] = pd.to_numeric(world['pop_2023'], errors='coerce').fillna(0)
world['area_sqkm'] = world.to_crs('+proj=cea').geometry.area / 10**6
world['pop_density'] = world['pop_2023'] / world['area_sqkm']


# ==========================================
# PART 1: PROJECTION CHALLENGE (3 Maps)
# Requirement Checklist: Reproject 3 times, Titles, Legends, Source Labels, Projection Notes
# ==========================================
print("\nGenerating Projection Challenge Maps...")

fig, axes = plt.subplots(3, 1, figsize=(12, 20))
fig.suptitle("Global Population Density: Analyzing Map Projections", fontsize=20, y=0.93)

# --- Map 1: Web Mercator (EPSG:3857) ---
world_mercator = world.to_crs("EPSG:3857")
world_mercator.plot(column='pop_density', ax=axes[0], cmap='YlOrRd', scheme='quantiles', k=5,
                    legend=True, legend_kwds={'loc': 'lower left', 'title': 'Pop per Sq Km'})
axes[0].set_title("1. Web Mercator (Conformal) - Heavy Area Distortion at Poles", fontsize=14)
axes[0].set_axis_off()
axes[0].text(0.01, 0.01, "Projection: Web Mercator (EPSG:3857) | Note: Greenland appears artificially massive.", 
             transform=axes[0].transAxes, fontsize=10, style='italic')

# --- Map 2: Equal Earth (EPSG:8857) ---
world_equal_area = world.to_crs("EPSG:8857")
world_equal_area.plot(column='pop_density', ax=axes[1], cmap='YlOrRd', scheme='quantiles', k=5,
                      legend=True, legend_kwds={'loc': 'lower left', 'title': 'Pop per Sq Km'})
axes[1].set_title("2. Equal Earth (Equal-Area) - Accurate Thematic Representation", fontsize=14)
axes[1].set_axis_off()
axes[1].text(0.01, 0.01, "Projection: Equal Earth (EPSG:8857) | Note: Preserves physical area perfectly.", 
             transform=axes[1].transAxes, fontsize=10, style='italic')

# --- Map 3: Robinson (+proj=robin) ---
world_robinson = world.to_crs("+proj=robin")
world_robinson.plot(column='pop_density', ax=axes[2], cmap='YlOrRd', scheme='quantiles', k=5,
                    legend=True, legend_kwds={'loc': 'lower left', 'title': 'Pop per Sq Km'})
axes[2].set_title("3. Robinson (Compromise) - Balanced for General Visuals", fontsize=14)
axes[2].set_axis_off()
axes[2].text(0.01, 0.01, "Projection: Robinson (+proj=robin) | Note: Balances shape and area distortion.", 
             transform=axes[2].transAxes, fontsize=10, style='italic')

# --- Requirement: Include Source Labels & Notes ---
fig.text(0.5, 0.05, "Data Source: Natural Earth & Mocked World Bank Data | Analysis by [Your Name]", 
         ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

# Save High-Resolution Output (Requirement)
plt.tight_layout(rect=[0, 0.08, 1, 0.92]) # Adjust layout to fit the bottom text
plt.savefig("Task1_Projection_Comparison.png", dpi=300, bbox_inches='tight')
print("Successfully exported high-resolution 'Task1_Projection_Comparison.png'.")
plt.show()