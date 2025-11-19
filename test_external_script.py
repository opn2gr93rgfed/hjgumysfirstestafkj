"""
Тестовый скрипт для проверки импорта
Данные пользователя: Adam Fisher jfeuheghuihegj9egh@gmail.com 10101900
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from elements_manager import *
from selenium.webdriver.common.keys import Keys
driver = webdriver.Chrome(ChromeDriverManager().install())
# to click on the element(www.testest.comVerifyi...) found
driver.find_element(By.XPATH,get_xpath(driver,'BJ05tXEOuu06m7Z')).click()

# to click on the element(Get started) found
driver.find_element(By.XPATH,get_xpath(driver,'gFKwmdpfrHzFK83')).click()

# to click on the element(First name) found
driver.find_element(By.XPATH,get_xpath(driver,'YIFjT9kq3o5PEb_')).click()

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'fYsTI13_rml3tMs')).send_keys('Adam')

# to click on the element(Last name) found
driver.find_element(By.XPATH,get_xpath(driver,'9Dz1_AOXH4zLZjG')).click()

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'wIKmzLjQdTQwQ05')).send_keys('Fisher')

# to click on input field
driver.find_element(By.XPATH,get_xpath(driver,'gPAMnDQ4ksvHus4')).click()

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'tJZm6UxdZNuMAQD')).send_keys('jfeuheghuihegj9egh@gmail.com')

# to click on the element(Next) found
driver.find_element(By.XPATH,get_xpath(driver,'TggRbY12jUkeBbU')).click()

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'Mcl9ZktzIHeZ8kH')).send_keys('10101900')

# to click on the element(Next) found
driver.find_element(By.XPATH,get_xpath(driver,'7t_1bOR89bInx2Y')).click()
