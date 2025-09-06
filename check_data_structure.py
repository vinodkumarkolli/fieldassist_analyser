import pandas as pd
import os

# Check the structure of the outlets file
outlets_files = os.listdir("Outlets")
if outlets_files:
    outlets_file = os.path.join("Outlets", outlets_files[0])
    print("Outlets file:", outlets_file)
    df = pd.read_excel(outlets_file, sheet_name=0)
    print("Outlets columns:", df.columns.tolist())
    print("Outlets shape:", df.shape)
    print("Outlets sample:")
    print(df.head(3))
    print("\n")

# Check the structure of the orders files
orders_files = os.listdir("Secondary Orders")
if orders_files:
    orders_file = os.path.join("Secondary Orders", orders_files[0])
    print("Orders file:", orders_file)
    df = pd.read_excel(orders_file, sheet_name=0)
    print("Orders columns:", df.columns.tolist())
    print("Orders shape:", df.shape)
    print("Orders sample:")
    print(df.head(3))
    print("\n")

# Check the structure of the visits files
visits_files = os.listdir("Visits")
if visits_files:
    visits_file = os.path.join("Visits", visits_files[0])
    print("Visits file:", visits_file)
    df = pd.read_excel(visits_file, sheet_name=0)
    print("Visits columns:", df.columns.tolist())
    print("Visits shape:", df.shape)
    print("Visits sample:")
    print(df.head(3))
    print("\n")