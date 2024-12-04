import os
import pandas as pd

# Directory containing the CSV files
directory = "./external_data/Berlin/"

# Initialize an empty list to store dataframes
dataframes = []

try:
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and filename.startswith("results-"):
            print(f"Processing {filename}")
            file_path = os.path.join(directory, filename)

            # Extract year from the filename (e.g., "results-2018.csv")
            year = filename.split("-")[1].split(".")[0]

            # Read the CSV file
            try:
                df = pd.read_csv(file_path)
                df["year"] = int(year)  # Add the year column
                dataframes.append(df)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # Merge all dataframes, aligning columns dynamically
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True, sort=False)

        # Specify the output path
        output_path = "results/merged_marathon_results.csv"

        # Save the merged DataFrame
        merged_df.to_csv(output_path, index=False)
        print(merged_df.values)
        print(f"File saved at: {output_path}")
    else:
        print("No dataframes to merge. Check if the directory contains valid CSV files.")
except Exception as e:
    print(f"An error occurred: {e}")
