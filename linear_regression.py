from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

file_path = "results/cleaned_marathon_data.csv"  # Replace with your actual file path
df = pd.read_csv(file_path, sep=";")

# Ensure we have the required data columns for regression
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
