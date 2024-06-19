from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from time import sleep

import os
import re
import requests
#import json
service = Service(executable_path='/root/chromedriver')
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  
chrome_options.add_argument("--no-sandbox")  # Required when running as root user
chrome_options.add_argument("--remote-debugging-port=9222")  # Specify a port for remote debugging
chrome_options.add_argument("--disable-dev-shm-usage")  # Required for Chrome to run properly in Docker
no_success = True
toggle = 0
while no_success:
    
    print("checking for available appointments...")


    driver = webdriver.Chrome(service = service, options=chrome_options)
    #driver = webdriver.Chrome(service=service)
    #driver = webdriver.Chrome()






    driver.get("https://ais.usvisa-info.com/en-ae/niv/users/sign_in")
    driver.refresh()
    toggle ^= 1
    email_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "user_email"))
    )

    # Input the email address
    
    email_input.send_keys("someemail@gmail.com")

    # Wait for the password input field to be visible
    password_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "user_password"))
    )

    # Input the password
    password_input.send_keys("somepassword!")

    # Wit for the policy confirmation checkbox to be clickable
    policy_checkbox = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "/html/body/div[5]/main/div[3]/div/div[1]/div/form/div[3]/label/div"))
    )

    # Click the policy confirmation checkbox
    policy_checkbox.click()

    #search.send_keys(Keys.SPACE)
    submit = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "/html/body/div[5]/main/div[3]/div/div[1]/div/form/p[1]/input"))
    )
    submit.click()
    sleep(2)

    try:
        button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Continue"))
        )
        button.click()

        button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Schedule Appointment"))
        )
        button.click()

        #another schedule Appointment which is subcategorie of Schedule Appointment
        button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/main/div[2]/div[2]/div/section/ul/li[1]/div/div/div[2]/p[2]/a"))
        )
        button.click()

        #Consular Section Location
        dropdown = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "appointments_consulate_appointment_facility_id"))
        )
        select = Select(dropdown)

        

    except Exception as e:
        print (e)
        no_success = False
        break

    sleep(2)

    json_data = ""
    consulate_path = ["49.json", "50.json"]
    consulate_location = ["49", "50"]
    print("choosing sefarat")
    while (no_success):
        try:
            dropdown = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "appointments_consulate_appointment_facility_id"))
            )
            select = Select(dropdown)

            select.select_by_value(consulate_location[int(toggle)])
            sleep(3)
            for request in driver.requests:
                # Check if the request is a JSON file
                if request.response and request.path.endswith(consulate_path[int(toggle)]):
                    # Access the JSON response
                    #print("requestpath = ", request.path)
                    json_data = request.response.body.decode('utf-8')
                    
                    # Access the status code of the response
                    status_code = request.response.status_code
                    #print(status_code)
            #check if there is any appointments at all
            dates = re.findall(r'"date":"(\d{4})-(\d{2})-(\d{2})"', json_data)
            appointments = [(month, day) for year, month, day in dates]
            current_day = datetime.now().day
            #print("dates = " , appointments)

            month = 0
            day = 1
            date_day = ""
            if not dates:
                #print("nicht gut diese")
                sleep(5)
                driver.close()
                break

            #check if there is any appointment in may or june
            for date in appointments:
                if date[month] == "05" or date[month] == "06":
                    date_day_int = int(date[day]) + 31 if int(current_day) > int(date[day]) else int(date[day])
                    #if there is time to apply for visa, set the corresponding day
                    if abs(int(current_day) - date_day_int) > 5 :
                        date_month = date[month]
                        date_day = date[day]
                        print("day = ", date_day)
                        print("month = ", date_month)
                        with open('sefarat_log.text', 'a') as file:
                            file.write(datetime.now().strftime("%B %d"))
                            file.write("-------> There exist an appointment\n")
                            # Write date_day and date_month
                            file.write("day = " + date_day + "\n")
                            file.write("month = " + date_month + "\n")
                        break
            if date_day == "":
                with open('sefarat_log.text', 'a') as file:
                            file.write(datetime.now().strftime("%H:%M") + ",     ")
                sleep(300)
                driver.close()
                break            
            
            #date_int = int(date_month+date_day)
            #date_month = date_int // 100
            #date_day = date_int % 100
            match date_month:
                case "05":
                    month_str = "May"
                    #date_day = date_int % 100
                case "06":
                    month_str = "June"
                    #date_day = date_int % 100
                case _:
                    if json_data != "[]":
                        sleep(300)
                        driver.close()
                        break
                    else:
                        sleep(3)
                        driver.close()
                        break

            dropdown.send_keys(Keys.TAB)
            # Loop to navigate to the desired month (December)
            current_month = driver.find_element(By.CLASS_NAME, 'ui-datepicker-month').text
            while current_month != month_str:
                try:
                    # Locate the "Next" button and click it
                    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ui-datepicker-next')))
                    next_button.click()
                    
                    # Check if the current month is December
                    current_month = driver.find_element(By.CLASS_NAME, 'ui-datepicker-month').text
                    print(current_month)
                    if current_month == month_str:
                        break  # Exit the loop if desired month is reached
                except Exception as e:
                    print(e)
                    driver.close()
                    no_success = False
                    break  # Exit the loop if unable to locate elements or other errors occur

            if current_month == month_str:
                print("date_day =", date_day)
                driver.find_element(By.LINK_TEXT, date_day).click()
                dropdown = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "appointments_consulate_appointment_time"))
                )
                select = Select(dropdown)
                sleep(3)
                print(select.first_selected_option.text) 
                select.select_by_index(1)
                sleep(3)
                submission_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'appointments_submit')))
                submission_button.click()
                no_success = False
                print("appointment Booked for", date_day, ".", month_str, select.all_selected_options[0].text)


                with open('sefarat_log.txt', 'a') as file:  # Corrected file name extension from .text to .txt
                    file.write(datetime.now().strftime("%H:%M ") + "\n")  # Add a space after the time
                    file.write("Appointment Booked for {} {}.{}".format(date_day, month_str, select.all_selected_options[0].text))  # Using format to insert variables

                print(select.first_selected_option.text)       
                #backup = "/root/sefarat-backup.sh"
                #os.remove(backup)
        except Exception as e:
            print(e)
            no_success = False
            break



driver.quit()




