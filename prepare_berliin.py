import pandas as pd


def time_to_seconds(time_str):
    if pd.isnull(time_str) or time_str == "00:00:00":
        return None  # Keep null for missing or invalid times
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s


file_path = 'results/merged_marathon_results_prepared.csv'
df = pd.read_csv(file_path, sep=';')
# List of time columns to process
time_columns = ['time_full', 'split_5k', 'split_10k', 'split_15k', 'split_20k',
                'time_half', 'split_25k', 'split_30k', 'split_35k', 'split_40k']

# Apply the time conversion to each relevant column
for col in time_columns:
    if col in df.columns:
        df[col] = df[col].apply(time_to_seconds)

# Save the cleaned DataFrame to a new CSV file
output_path = "results/cleaned_marathon_data.csv"
df.to_csv(output_path, index=False, sep=';')

print(f"Processed file saved as: {output_path}")
