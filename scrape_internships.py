from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_internships():
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
    url = 'https://internshala.com/internships'
    driver.get(url)

    try:
        # Wait until the internships section is present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'internship_meta'))
        )

        # Get the page source after content has loaded
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        internships = []
        internships_list = soup.find_all('div', class_='internship_meta')  # Ensure this matches the correct structure

        for internship in internships_list:
            # Extract Title
            title_element = internship.find('h3', class_='job-internship-name')
            title = title_element.get_text(strip=True) if title_element else "N/A"
            
            # Extract Location
            location_element = internship.find('div', class_='row-1-item locations')
            location = location_element.get_text(strip=True) if location_element else "N/A"

            # Extract Salary Expectation
            stipend_element = internship.find('span', class_='stipend')
            stipend = stipend_element.get_text(strip=True) if stipend_element else "N/A"

            # Extract Duration
            duration_element = internship.find('div', class_='row-1-item')  # Adjust to target the correct duration
            duration = duration_element.get_text(strip=True) if duration_element else "N/A"
            
            internships.append({
                'title': title,
                'location': location,
                'stipend': stipend,
                'duration': duration
            })

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Ensure the driver is closed even if an error occurs

    return internships

if __name__ == '__main__':
    data = scrape_internships()
    for internship in data:
        print(internship)