import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Chrome()

try:
    driver.get('https://www.redbus.in/online-booking/rsrtc')
    driver.maximize_window()
    driver.implicitly_wait(10)

    # Initialize variables to store collected data and track route names
    previously_collected_data = []
    collected_route_names = set()

    scrolling = True
    scroll_pause_time = 2

    while scrolling:
        old_page_source = driver.page_source
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(scroll_pause_time)
        new_page_source = driver.page_source

        if new_page_source == old_page_source:
            scrolling = False

        # Get all links on the page with class="route"
        all_links = driver.find_elements(By.XPATH, '//a[@class="route"]')

        for link in all_links:
            route_name = link.text.strip()
            route_link = link.get_attribute("href")
            # Check if route name is not empty and is not already collected
            if route_name and route_link and route_name not in collected_route_names:
                previously_collected_data.append({"route_name": route_name, "route_link": route_link})
                collected_route_names.add(route_name)  # Add route name to set to track duplicates

    # Function to navigate to a specific page number
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

    # Navigate through pages 1 to 2
    for page_number in range(1,4):
        navigate_to_page(driver, page_number)
        time.sleep(3)

        scrolling = True
        while scrolling:
            old_page_source = driver.page_source
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(scroll_pause_time)
            new_page_source = driver.page_source

            if new_page_source == old_page_source:
                scrolling = False

            # Get all links on the page with class="route"
            all_links = driver.find_elements(By.XPATH, '//a[@class="route"]')

            for link in all_links:
                route_name = link.text.strip()
                route_link = link.get_attribute("href")
                # Check if route name is not empty and is not already collected
                if route_name and route_link and route_name not in collected_route_names:
                    previously_collected_data.append({"route_name": route_name, "route_link": route_link})
                    collected_route_names.add(route_name)  # Add route name to set to track duplicates

    # Save data to a CSV file
    file_path = r'C:\Users\ediso\OneDrive\Desktop\Data_science\Project\bus_routes.csv'
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Bus_Route_Name', 'Route_Link'])
        for data in previously_collected_data:
            writer.writerow([data["route_name"], data["route_link"]])

    print(f'CSV file saved at: {file_path}')

finally:
    time.sleep(5)
    driver.quit()
