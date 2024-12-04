import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def get_top_100_runners(df):
    df = df.dropna(subset=['place_overall'])
    df['place_overall'] = pd.to_numeric(df['place_overall'], errors='coerce')

    top_100_runners = (
        df.sort_values(by=['year', 'place_overall'])
        .groupby('year')
        .head(100)
    )

    # Display the new DataFrame
    return top_100_runners


# Load the dataset with semicolon delimiters
file_path = "results/cleaned_marathon_data.csv"  # Replace with your actual file path
df = pd.read_csv(file_path, sep=";")

# Convert times from seconds to minutes for visualization if already in seconds
if 'time_full' in df.columns:
    df['time_full_minutes'] = df['time_full'] / 60

# df = get_top_100_runners(df)

# Example Analysis: Average finishing time by gender
if 'gender' in df.columns:
    avg_time_by_gender = df.groupby("gender")["time_full_minutes"].mean()

    plt.figure(figsize=(8, 5))
    avg_time_by_gender.plot(kind="bar", color=["blue", "orange"], alpha=0.7)
    plt.title("Average Finish Time by Gender")
    plt.ylabel("Finish Time (Minutes)")
    plt.xlabel("Gender")
    plt.xticks(rotation=0)
    plt.show()

# Example Analysis: Finishing time trends over the years (scatter plot without connecting dots)
if 'year' in df.columns and 'time_full_minutes' in df.columns:
    plt.figure(figsize=(8, 5))
    for gender in df["gender"].unique():
        gender_data = df[df["gender"] == gender]
        plt.scatter(gender_data["year"], gender_data["time_full_minutes"], label=f"Gender: {gender}", alpha=0.7)

    plt.title("Finishing Time Trends Over the Years")
    plt.ylabel("Finish Time (Minutes)")
    plt.xlabel("Year")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()


# Example Analysis: Nationality distribution among top runners (filtering low counts)
if 'nationality' in df.columns:
    # Filter out nationalities with 20 or fewer occurrences
    nationality_counts = df["nationality"].value_counts()
    filtered_counts = nationality_counts[nationality_counts > 10_000]

    plt.figure(figsize=(8, 5))
    filtered_counts.plot(kind="bar", color="green", alpha=0.7)
    plt.title("Nationality Distribution of Top Runners (Excluding Low Counts)")
    plt.ylabel("Count")
    plt.xlabel("Nationality")
    plt.xticks(rotation=0)
    plt.show()
else:
    print("The 'nationality' column is not available in the dataset.")

# Example Analysis: Average finish time over the years as a box plot
if 'year' in df.columns and 'time_full_minutes' in df.columns:
    plt.figure(figsize=(10, 6))
    df.boxplot(column='time_full_minutes', by='year', grid=False, notch=True)
    plt.title("Finish Time Distribution Over the Years")
    plt.suptitle("")  # Remove the default Pandas boxplot subtitle
    plt.ylabel("Finish Time (Minutes)")
    plt.xlabel("Year")
    plt.xticks(rotation=45)
    plt.show()
else:
    print("The required columns 'year' and 'time_full_minutes' are not available in the dataset.")


required_columns = ['time_full', 'split_5k', 'split_10k', 'split_15k', 'split_20k']
if all(col in df.columns for col in required_columns):
    # Drop rows with missing values in the required columns
    df_cleaned = df[required_columns].dropna()

    # Define features (X) and target (y)
    X = df_cleaned[['split_5k', 'split_10k', 'split_15k', 'split_20k']]
    y = df_cleaned['time_full']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Display the results
    print("Linear Regression Results:")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"R-squared (R2 Score): {r2:.2f}")

    # Visualize actual vs predicted times
    plt.figure(figsize=(8, 5))
    plt.scatter(y_test, y_pred, alpha=0.7)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.title("Actual vs Predicted Finish Times")
    plt.xlabel("Actual Finish Time (seconds)")
    plt.ylabel("Predicted Finish Time (seconds)")
    plt.grid(alpha=0.3)
    plt.show()
else:
    print("Required columns for linear regression are not available in the dataset.")
