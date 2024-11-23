import pandas as pd
import random

# Load the Excel file
file_path = "data/data.xlsx"  # Replace with your Excel file path
df = pd.read_excel(file_path)

# Define the four random numbers
random_numbers = [48273, 15947, 69351, 20486]

# Fill the 'user_code' column with random selections from the numbers
df['user_code'] = [random.choice(random_numbers) for _ in range(len(df))]

# Save the modified Excel file
output_path = "data/op.xlsx"  # Define the output file path
df.to_excel(output_path, index=False)

print("Excel file updated with random 'user_code' values and saved as", output_path)
