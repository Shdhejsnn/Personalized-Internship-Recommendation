import pandas as pd
import re
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report
import joblib  # To save and load the model

# Load the preprocessed internship data
internship_data = pd.read_excel('data/preprocessed_internship_data.xlsx')

# Clean column names
internship_data.columns = internship_data.columns.str.strip()

# Clean stipend function
def clean_stipend(stipend):
    stipend = re.sub(r'[₹/month ]', '', stipend)
    stipend = stipend.replace(',', '')
    try:
        if '-' in stipend:
            min_value, max_value = map(float, stipend.split('-'))
            return (min_value + max_value) / 2
        else:
            return float(stipend)
    except ValueError:
        return None

# Apply cleaning function to stipend column
internship_data['Cleaned_Stipend'] = internship_data['Stipend'].apply(clean_stipend)

# Ensure 'Apply By' is in datetime format
internship_data['Apply By'] = pd.to_datetime(internship_data['Apply By'], errors='coerce')

# Prepare feature and target variables
np.random.seed(42)
internship_data['User_Liked'] = np.random.choice([0, 1], size=len(internship_data))

# Define the tokenizer function
def custom_tokenizer(x):
    return x.split(', ')

# One-hot encoding for locations
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
location_features = encoder.fit_transform(internship_data[['Location']])

# Count vectorization for skills
vectorizer = CountVectorizer(tokenizer=custom_tokenizer)
skills_features = vectorizer.fit_transform(internship_data['Skills Required']).toarray()

# Combine features into a single array
X = np.hstack((location_features, skills_features, internship_data[['Cleaned_Stipend']].values))
y = internship_data['User_Liked'].values

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, 'internship_recommendation_model.pkl')
joblib.dump(encoder, 'location_encoder.pkl')
joblib.dump(vectorizer, 'skills_vectorizer.pkl')

# Evaluate the model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Define the recommend_internships function
def recommend_internships(user_skills, user_locations, preferred_duration, min_stipend, max_stipend):
    matching_internships = []

    # Load the model and encoders
    model = joblib.load('internship_recommendation_model.pkl')
    encoder = joblib.load('location_encoder.pkl')
    vectorizer = joblib.load('skills_vectorizer.pkl')

    # Vectorize user skills and compute average stipend
    user_skills_vectorized = vectorizer.transform([', '.join(user_skills)]).toarray()
    user_stipend = np.array([[min_stipend + (max_stipend - min_stipend) / 2]])  # Average stipend

    # Iterate through the internships and filter by user's input (duration, stipend range)
    for index, internship_info in internship_data.iterrows():
        # Extract and process internship skills
        internship_skills = internship_info['Skills Required']  # This should be a list
        if isinstance(internship_skills, str):
            internship_skills = eval(internship_skills)  # Convert string representation of list to list

        # Check for any matching skills
        skill_match = any(skill.strip().lower() in (s.lower() for s in internship_skills) for skill in user_skills)

        # Filter by duration and stipend range
        if (internship_info['Duration'] < preferred_duration) or \
           (internship_info['Cleaned_Stipend'] < min_stipend) or \
           (internship_info['Cleaned_Stipend'] > max_stipend):
            continue  # Skip internships that don't match the filter

        # If there's a skill match, we consider the internship for recommendation
        if skill_match:
            # Encode internship location
            internship_location = internship_info['Location'].lower().strip()
            internship_location_encoded = encoder.transform([[internship_location]])

            # Vectorize the internship skills
            internship_skills_vectorized = vectorizer.transform([' '.join(internship_skills)]).toarray()
            internship_stipend = np.array([[internship_info['Cleaned_Stipend']]])

            # Combine internship features
            internship_features = np.hstack((internship_location_encoded, internship_skills_vectorized, internship_stipend))

            # Predict using the model
            prediction = model.predict(internship_features)

            # If the model predicts the user would like the internship, append it to the result
            if prediction[0] == 1:
                matching_internships.append({
                    "Company": internship_info['Company'],
                    "Profile": internship_info['Profile'],
                    "Stipend": internship_info['Stipend'],
                    "Duration": internship_info['Duration'],
                    "Location": internship_info['Location'],
                    "Apply By": internship_info['Apply By']  # Include Apply By date
                })

    # Sort internships by 'Apply By' date
    matching_internships.sort(key=lambda x: x['Apply By'])

    return matching_internships
