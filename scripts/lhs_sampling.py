"""
=========================================================
VenturiFlowLab
Latin Hypercube Sampling (LHS)

Author : Aakash
Project: VenturiFlowLab

Description:
Generates 100 Venturi geometries using Latin Hypercube
Sampling based on literature-defined parameter ranges.

Output:
data/venturi_samples.csv
=========================================================
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import qmc

# ==========================================================
# USER SETTINGS
# ==========================================================

NUMBER_OF_SAMPLES = 100

THROAT_DIAMETER = 20.0      # Fixed (mm)

# Parameter ranges (based on literature review)

parameter_ranges = {
    "Inlet Diameter": (35.0, 50.0),      # mm
    "Outlet Diameter": (45.0, 70.0),     # mm
    "Converging Angle": (6.0, 16.0),     # degrees
    "Diverging Angle": (5.0, 10.0),      # degrees
    "Throat Length": (5.0, 12.0)         # mm
}

# ==========================================================
# CREATE OUTPUT DIRECTORY
# ==========================================================

os.makedirs("data", exist_ok=True)

# ==========================================================
# LATIN HYPERCUBE SAMPLING
# ==========================================================

print("\nGenerating Latin Hypercube Samples...\n")

sampler = qmc.LatinHypercube(
    d=len(parameter_ranges),
    seed=42
)

lhs_samples = sampler.random(NUMBER_OF_SAMPLES)

# ==========================================================
# SCALE TO REAL DIMENSIONS
# ==========================================================

columns = list(parameter_ranges.keys())

scaled_samples = np.zeros_like(lhs_samples)

for i, parameter in enumerate(columns):

    lower, upper = parameter_ranges[parameter]

    scaled_samples[:, i] = (
        lower + lhs_samples[:, i] * (upper - lower)
    )

# ==========================================================
# CREATE DATAFRAME
# ==========================================================

df = pd.DataFrame(
    scaled_samples,
    columns=columns
)

# Add Design ID

df.insert(
    0,
    "ID",
    range(1, NUMBER_OF_SAMPLES + 1)
)

# Fixed throat diameter

df.insert(
    3,
    "Throat Diameter",
    THROAT_DIAMETER
)

# Round values

df = df.round(2)

# ==========================================================
# SAVE CSV
# ==========================================================

output_file = "data/venturi_samples.csv"

df.to_csv(
    output_file,
    index=False
)

# ==========================================================
# DISPLAY RESULTS
# ==========================================================

print("=================================================")
print(" VenturiFlowLab")
print(" Latin Hypercube Sampling Complete")
print("=================================================\n")

print(f"Number of Samples : {NUMBER_OF_SAMPLES}")

print(f"Output File       : {output_file}")

print("\nParameter Ranges\n")

for parameter, values in parameter_ranges.items():

    print(f"{parameter:20s} : {values[0]}  -->  {values[1]}")

print("\nFirst Five Samples\n")

print(df.head())

print("\nDone!")
