import os
import pandas as pd

# Set the root directory
root_dir = './batch_teste'

# Initialize an empty DataFrame for aggregation
aggregated_data = pd.DataFrame()
count=0
# Iterate through all subfolders
for subdir, _, files in os.walk(root_dir):
    # Check if "resultado.csv" is present in the current subfolder
    if 'resultado.csv' in files:
        # Construct the full path to the CSV file
        csv_path = os.path.join(subdir, 'resultado.csv')
        # Assuming df is your DataFrame and "event_type" is the column name

# Print the lines where event_type is 'esprial'
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)
#        print(df)

        count=count+1
        sigma,sf=df.iloc[0]["Sigma"],float(df.iloc[0]["Sigma_Factor"].strip("[]"))
        # Aggregate data by appending to the main DataFrame
        aggregated_data = aggregated_data._append(df.iloc[1:], ignore_index=True)

# Save the aggregated data to a new CSV file
aggregated_data.to_csv('aggregated_result.csv', index=False)
spiral_lines = aggregated_data[aggregated_data['Event_Type'] == 'Espiral']

spiral_lines.to_csv('spiral_lines.csv', index=False)

print("Simulacoes feitas: ",count)
print("Espirais encontradas")
print(spiral_lines)
