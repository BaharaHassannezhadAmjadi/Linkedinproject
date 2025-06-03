from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os


class JobListingScraper:
    def __init__(self, job_title, max_results = 10, location_filter = None, experience_filter = None):
        self.job_title = job_title
        self.max_results = max_results
        self.location_filter = location_filter.lower() if location_filter else None
        self.experience_filter = experience_filter.lower() if experience_filter else None
        self.driver = self._init_driver()
        self.jobs_data = [] 

    def _init_driver(self):
        options = Options()  
        options.add_argument("--start-maximized")  
        service = Service("C:\\Users\\MASOUD\Desktop\Linkedinproject\\chromedriver.exe")
        return webdriver.Chrome(service = service, options = options)
    
    def search_jobs(self):
        query = self.job_title.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}"
        self.driver.get(url)
        time.sleep(5)

    def matches_filters(self, location, description_text):
        if self.location_filter and self.location_filter not in location.lower():
            return False
        if self.experience_filter and self.experience_filter not in description_text.lower():
            return False 
        return True

    def scrape_jobs(self):
        job_cards = self.driver.find_elements(By.CLASS_NAME, 'base-card')[:self.max_results]
        for card in job_cards:
            try:
                title = card.find_element(By.CLASS_NAME, 'base-search-card__title').text.strip()
                company = card.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text.strip()
                location = card.find_element(By.CLASS_NAME, 'job-search-card__location').text.strip()
                link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')

                self.driver.execute_script("window.open(arguments[0]);", link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(2)

                try:
                    description = self.driver.find_element(By.CLASS_NAME, 'description__text').text.lower()
                except:
                    description = ""

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0]) 

                if not self.matches_filters(location, description): 
                    continue

                self.jobs_data.append({
                    'Job Title': title,
                    'Company': company,
                    'Location': location,
                    'Link': link
                })

            except:
                continue

    def save_to_csv(self):
        df = pd.DataFrame(self.jobs_data)
        filename = f"{self.job_title.replace(' ', '_')}_filtered_jobs.csv" 
        df.to_csv(filename, index = False)
        full_path = os.path.abspath(filename)
        print(f"CSV saved to: {full_path}")
        os.startfile(full_path)
        

    def run(self):
        self.search_jobs()
        self.scrape_jobs()
        self.save_to_csv()
        self.driver.quit()


if __name__ == "__main__":
    job_title = input("Enter job title (e.g., Data Scientist): ")
    max_results = input("Max number of results to fetch: ")
    location_filter = input("Filter by location (optional, e.g., Tehran or Remote): ")
    experience_filter = input("Filter by experience (optional: Entry, Mid, Senior): ")

    try:
        max_results = int(max_results)
    except:
        max_results = 10

    scraper = JobListingScraper(
        job_title = job_title,
        max_results = max_results,
        location_filter = location_filter,
        experience_filter = experience_filter
    ) 
    scraper.run()                                