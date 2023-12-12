import pandas as pd

def average_salary_data(input_csv_file, output_csv_file):
    # Load the CSV data into a DataFrame
    df = pd.read_csv(input_csv_file)
    df = df.dropna(subset=['salary_type', 'ten_percentile_salary', 'ninety_percentile_salary', 'fifty_percentile_salary'], how='all')
    # Group by 'salary_id' and 'salary_type', then calculate the mean for the salary columns
    averaged_df = df.groupby(['id', 'salary_type']).mean().reset_index()

    # Save the averaged data into a new CSV file
    averaged_df.to_csv(output_csv_file, index=False)

import pandas as pd

import pandas as pd

def create_sql_for_deleting_entries(input_csv_file, sql_output_file):
    # Load the CSV data into a DataFrame
    df = pd.read_csv(input_csv_file)

    # Define salary columns to check
    salary_columns = ['ten_percentile_salary', 'ninety_percentile_salary', 'fifty_percentile_salary']

    # Filter for rows where salary information is all NaN or empty but the ID is not NaN or empty
    ids_to_delete = df[df[salary_columns].isna().all(axis=1) & df['id'].notna()]['id']

    # Convert the Series to a list and then to a string format suitable for SQL IN clause
    ids_list_str = ', '.join(map(str, ids_to_delete.tolist()))

    if ids_list_str:  # Check if the string is not empty
        # Open the SQL output file for writing
        with open(sql_output_file, 'w') as file:
            # Write SQL statements to delete entries from both tables in a single transaction
            file.write("BEGIN;\n")
            file.write(f"DELETE FROM review WHERE id IN (SELECT review_id FROM job WHERE salary_id IN ({ids_list_str}));\n")
            file.write(f"DELETE FROM job WHERE salary_id IN ({ids_list_str});\n")
            file.write("COMMIT;\n")
    else:
        print("No IDs found for deletion.")

# Example usage
# create_sql_for_deleting_entries('input_file.csv', 'delete_entries.sql')

# create_sql_for_deleting_entries('input_file.csv', 'delete_entries.sql')


# Example usage
# extract_ids_with_no_salary_info('input_file.csv', 'missing_salary_ids.csv')

# Example usage
create_sql_for_deleting_entries('C:/Users/Samue/Downloads/archive/Salaries.csv', 'C:/Users/Samue/Downloads/archive/Salary3.sql')
