import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime, date

# Initialize WebDriver
driver = webdriver.Chrome()

def navigate_to_page(driver, page_number):
    try:
        pagination_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".DC_117_paginationTable"))
        )
        next_page_button = pagination_container.find_element(
            By.XPATH, f".//div[contains(@class, 'DC_117_pageTabs') and text()='{page_number}']")
        actions = ActionChains(driver)
        actions.move_to_element(next_page_button).perform()
        next_page_button.click()
        print(f"Navigated to page {page_number}")
    except Exception as e:
        print(f'Error navigating to page {page_number}: {e}')

def scroll_to_bottom(driver, pause_time=2):
    scrolling = True
    while scrolling:
        old_page_source = driver.page_source
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(pause_time)
        new_page_source = driver.page_source
        if new_page_source == old_page_source:
            scrolling = False

def collect_bus_data(driver, link_text):
    collected_data = []
    try:
        # Check if no buses found message is present
        no_buses_msg = driver.find_elements(By.CSS_SELECTOR, "div.msg")
        if no_buses_msg and len(no_buses_msg) > 0 and "Oops! No buses found." in no_buses_msg[0].text:
            print(f"No buses found for: {link_text}")
            collected_data.append({
                'bus_route_name': link_text,
                'bus_name': "Oops! No buses found.",
                'bus_type': "",
                'departure_time': "",
                'duration': "",
                'reaching_time': "",
                'star_rating': "",
                'price': "",
                'seat_availability': ""
            })
            return collected_data  # Skip collecting detailed data if no buses found

        # Keep scrolling to load all buses
        scroll_to_bottom(driver, pause_time=0.02)

        # Collect bus elements
        bus_elements = driver.find_elements(By.CSS_SELECTOR, ".clearfix.row-one")

        for bus_element in bus_elements:
            bus_route_name = link_text  # Use the link text as the bus route name
            bus_name = bus_element.find_element(By.CSS_SELECTOR, ".travels.lh-24.f-bold.d-color").text.strip()
            bus_type_element = bus_element.find_element(By.CSS_SELECTOR, "div.bus-type.f-12.m-top-16.l-color.evBus")
            bus_type = bus_type_element.text.strip()
            departure_time_str = bus_element.find_element(By.CSS_SELECTOR, ".dp-time.f-19.d-color.f-bold").text.strip()
            duration = bus_element.find_element(By.CSS_SELECTOR, ".dur.lh-24").text.strip()
            reaching_time_str = bus_element.find_element(By.CSS_SELECTOR, ".bp-time.f-19.d-color.disp-Inline").text.strip()
            star_rating = bus_element.find_element(By.CSS_SELECTOR, ".rating-sec").text.strip()
            price = bus_element.find_element(By.CSS_SELECTOR, "span.f-19.f-bold, span.f-bold.f-19").text.strip()
            seat_availability = bus_element.find_element(By.CSS_SELECTOR, ".column-eight.w-15.fl").text.strip()

            # Get the current date
            today_date = date.today()

            # Combine the current date with the time strings
            departure_time = datetime.combine(today_date, datetime.strptime(departure_time_str, "%H:%M").time())
            reaching_time = datetime.combine(today_date, datetime.strptime(reaching_time_str, "%H:%M").time())

            collected_data.append({
                'bus_route_name': bus_route_name,
                'bus_name': bus_name,
                'bus_type': bus_type,
                'departure_time': departure_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration': duration,
                'reaching_time': reaching_time.strftime("%Y-%m-%d %H:%M:%S"),
                'star_rating': star_rating,
                'price': price,
                'seat_availability': seat_availability
            })

        print(f'Collected data for: {link_text}')
    except Exception as e:
        print(f"Error processing {link_text}: {str(e)}")
    return collected_data

try:
    # Navigate to the first page URL
    driver.get('https://www.redbus.in/online-booking/bsrtc-operated-by-vip-travels')
    driver.maximize_window()
    driver.implicitly_wait(10)

    collected_data = []

    # Navigate through pages 1 to 2
    for page_number in range(1, 2):
        navigate_to_page(driver, page_number)
        time.sleep(3)
        scroll_to_bottom(driver)

        # Fetch all route links dynamically using XPath
        link_elements = driver.find_elements(By.XPATH, "//a[@class='route']")
        links_to_click = [(element.text, element.get_attribute('href')) for element in link_elements if element.text]

        for link_text, link_url in links_to_click:
            driver.get(link_url)
            print(f'Navigated to: {link_text}')
            time.sleep(5)  # Adjust sleep time as necessary

            collected_data.extend(collect_bus_data(driver, link_text))

            # Navigate back to the main page URL after collecting data
            driver.get('https://www.redbus.in/online-booking/bsrtc-operated-by-vip-travels')
            time.sleep(5)  # Adjust sleep time as necessary for page load

    # Save the collected data to a CSV file
    file_path = r'C:\Users\ediso\OneDrive\Desktop\Data_science\Project\bus_routes.csv'
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['bus_route_name', 'bus_name', 'bus_type', 'departure_time', 'duration', 'reaching_time', 'star_rating', 'price', 'seat_availability'])
        writer.writeheader()
        for data in collected_data:
            writer.writerow(data)

    print(f'CSV file saved at: {file_path}')

finally:
    time.sleep(5)
    driver.quit()
