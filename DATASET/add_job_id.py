import pandas as pd

# Read the input CSV file
df = pd.read_csv('Job.csv')

# Add an 'id' field to each row
df['id'] = range(1, len(df) + 1)

# Save the modified DataFrame to a new CSV file
df.to_csv('Job2.csv', index=False)