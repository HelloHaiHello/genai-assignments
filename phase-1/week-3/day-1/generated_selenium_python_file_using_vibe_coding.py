Feature: Create Lead

  Scenario Outline: Successful creation of lead with valid details
    Given I open the create lead page
    When I type "<company_name>" into the Company Name field
    And I type "<first_name>" into the First Name field
    And I type "<last_name>" into the Last Name field
    And I click the Create Lead button
    Then I should see the created lead details

  Examples:
    | company_name    | first_name | last_name |
    | "TCS"            | "Rajesh"   | "Kumar"   |
    | "Infosys"        | "Suresh"   | "Rao"     |
    | "Wipro"          | "Mahesh"   | "Reddy"   |

import pytest
from pytest_bdd import given, when, then, scenarios, scenario
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from typing import Optional

# Load all scenarios from feature file
scenarios('../features/create_lead.feature')

@pytest.fixture
def driver():
    """
    Pytest fixture to initialize and clean up WebDriver.
    """
    chrome_driver = webdriver.Chrome()
    chrome_driver.maximize_window()
    yield chrome_driver
    chrome_driver.quit()

@pytest.fixture
def wait(driver):
    """
    Pytest fixture to provide WebDriverWait instance.
    """
    return WebDriverWait(driver, timeout=10)

@given("I open the create lead page")
def open_create_lead_page(driver):
    """
    Open the create lead page.
    """
    driver.get("https://leaftaps.com/crmsfa/control/createLeadForm")

@when('I type "<company_name>" into the Company Name field')
def enter_company_name(driver, wait, company_name: str):
    """
    Enter company name in the Company Name field.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        company_name: Company name to enter
    """
    element = wait.until(
        EC.presence_of_element_located((By.ID, "createLeadForm_companyName"))
    )
    element.clear()
    element.send_keys(company_name)

@when('I type "<first_name>" into the First Name field')
def enter_first_name(driver, wait, first_name: str):
    """
    Enter first name in the First Name field.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        first_name: First name to enter
    """
    element = wait.until(
        EC.presence_of_element_located((By.ID, "createLeadForm_firstName"))
    )
    element.clear()
    element.send_keys(first_name)

@when('I type "<last_name>" into the Last Name field')
def enter_last_name(driver, wait, last_name: str):
    """
    Enter last name in the Last Name field.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        last_name: Last name to enter
    """
    element = wait.until(
        EC.presence_of_element_located((By.ID, "createLeadForm_lastName"))
    )
    element.clear()
    element.send_keys(last_name)

@when("I click the Create Lead button")
def click_create_lead_button(driver, wait):
    """
    Click the Create Lead button.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    """
    button = wait.until(
        EC.element_to_be_clickable((By.ID, "ext-gen538"))
    )
    button.click()

@then("I should see the created lead details")
def verify_lead_creation(driver, wait):
    """
    Verify successful lead creation by checking for success element.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    """
    # Add your logic to verify lead creation
    # For example, you can check for a specific element or text on the page
    success_element = wait.until(
        EC.visibility_of_element_located((By.TAG_NAME, "h2"))
    )
    assert success_element.is_displayed()