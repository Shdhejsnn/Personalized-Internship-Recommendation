from flask import Flask, render_template, request, redirect, url_for, flash 
from recommendation import recommend_internships  
import pandas as pd
import ast
import os  
app = Flask(__name__, static_folder='static')
app.secret_key = 'favicon'  

internship_data = pd.read_excel('data/preprocessed_internship_data.xlsx')
internship_data['Skills Required'] = internship_data['Skills Required'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

applications_file_path = 'data/applied_students.xlsx'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/try-now')
def try_now():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_skills_input = request.form.get('skills', '').strip()
    user_location_input = request.form.get('location', '').strip()
    preferred_duration_input = request.form.get('duration', '').strip()

    
    if not user_skills_input or not user_location_input or not preferred_duration_input:
        return render_template('index.html', error="Please provide skills, location, and preferred duration.")

    
    preferred_duration = preferred_duration_input  

    try:
        min_stipend = int(request.form.get('min_stipend', 0))
        max_stipend = int(request.form.get('max_stipend', 0))
        if min_stipend < 0 or max_stipend < 0:
            return render_template('index.html', error="Stipend values must be non-negative.")
        if min_stipend > max_stipend:
            return render_template('index.html', error="Minimum stipend should not exceed maximum stipend.")
    except ValueError:
        return render_template('index.html', error="Please enter valid numeric stipend values.")

    
    user_skills = [skill.strip().lower() for skill in user_skills_input.split(',') if skill.strip()]  # Filter out empty skills
    user_locations = [location.strip().lower() for location in user_location_input.split(',') if location.strip()]  # Filter out empty locations

    
    recommended_internships = recommend_internships(user_skills, user_locations, preferred_duration, min_stipend, max_stipend)

   
    if not recommended_internships:
        return render_template('index.html', error="No internships found matching your criteria.")

    
    return render_template('recommendation.html', internships=recommended_internships)

@app.route('/internship/<string:company_name>', methods=['GET', 'POST'])
def internship_detail(company_name):
    internships = internship_data.loc[internship_data['Company'].str.lower() == company_name.lower()].to_dict(orient='records')

    if internships:
        internship = internships[0]  

        if isinstance(internship['Skills Required'], str):
            internship['Skills Required'] = [skill.strip() for skill in internship['Skills Required'].split(',')]

        if request.method == 'POST':
            applicant_first_name = request.form['first_name']  # First Name
            applicant_last_name = request.form['last_name']    # Last Name
            applicant_email = request.form['email']            # Email
            applicant_contact_number = request.form['contact_number']  
            applicant_current_city = request.form['current_city']      
            applicant_gender = request.form['gender']                  

          
            if not applicant_first_name or not applicant_last_name or not applicant_email or not applicant_contact_number or not applicant_current_city or not applicant_gender:
                return render_template('internship_detail.html', internship=internship, error="Please fill in all fields.")

        
            save_application({
                "internship_company": internship['Company'],
                "first_name": applicant_first_name,
                "last_name": applicant_last_name,
                "email": applicant_email,
                "contact_number": applicant_contact_number,
                "current_city": applicant_current_city,
                "gender": applicant_gender
            })

     
            flash("Your application has been submitted successfully!")
            return redirect(url_for('index'))

        return render_template('internship_detail.html', internship=internship)
    else:
        return "Internship not found", 404

@app.route('/apply/<string:company_name>', methods=['GET', 'POST'])
def apply(company_name):
    internships = internship_data.loc[internship_data['Company'].str.lower() == company_name.lower()].to_dict(orient='records')

    if internships:
        internship = internships[0] 

        if request.method == 'POST':
            applicant_first_name = request.form['first_name']
            applicant_last_name = request.form['last_name']
            applicant_email = request.form['email']
            applicant_contact_number = request.form['contact_number']
            applicant_current_city = request.form['current_city']
            applicant_gender = request.form['gender']

         
            if not applicant_first_name or not applicant_last_name or not applicant_email or not applicant_contact_number or not applicant_current_city or not applicant_gender:
                return render_template('apply.html', internship=internship, error="Please fill in all fields.")

           
            save_application({
                "internship_company": internship['Company'],
                "first_name": applicant_first_name,
                "last_name": applicant_last_name,
                "email": applicant_email,
                "contact_number": applicant_contact_number,
                "current_city": applicant_current_city,
                "gender": applicant_gender
            })

            flash("Your application has been submitted successfully!")
            return redirect(url_for('index'))

        return render_template('apply.html', internship=internship)
    else:
        return "Internship not found", 404

def save_application(application):
  
    application_df = pd.DataFrame([application])

    if os.path.exists(applications_file_path):
   
        existing_df = pd.read_excel(applications_file_path)
        updated_df = pd.concat([existing_df, application_df], ignore_index=True)
        updated_df.to_excel(applications_file_path, index=False)  
    else:
        application_df.to_excel(applications_file_path, index=False)

if __name__ == '__main__':
    app.run(debug=True)
