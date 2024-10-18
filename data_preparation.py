import pandas as pd
import ast

def preprocess_internship_data(internship_data):
    # Drop 'Sno' and 'Unnamed: 7' columns if they exist
    columns_to_drop = ['Sno', 'Unnamed: 7']
    internship_data.drop(columns=[col for col in columns_to_drop if col in internship_data.columns], inplace=True)

    # Ensure 'Skills Required' is a list
    internship_data['Skills Required'] = internship_data['Skills Required'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    # Convert skills to lowercase and strip whitespace
    internship_data['Skills Required'] = internship_data['Skills Required'].apply(
        lambda skills: [skill.strip().lower() for skill in skills]
    )
    internship_data['Location'] = internship_data['Location'].str.strip()

    # Update 'Apply By' column with 3-day gaps for every 10 entries
    base_date = pd.Timestamp('2024-10-20')
    day_interval = 1
    
    # Create a function to generate dates
    def generate_apply_by_dates(index):
        return base_date + pd.DateOffset(days=(index // 30) * day_interval)

    # Apply the function to the 'Apply By' column and format as '20th Oct 24'
    internship_data['Apply By'] = internship_data.index.map(generate_apply_by_dates).strftime('%d %b %y')

    return internship_data

# Load the internship data
internship_data = pd.read_excel('data/internship_data.xlsx')

# Preprocess the internship data
internship_data = preprocess_internship_data(internship_data)

# Save the preprocessed data
internship_data.to_excel('data/preprocessed_internship_data.xlsx', index=False)
