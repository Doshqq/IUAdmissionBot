from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def select_dropdown_item(driver, button_text: str, option_text: str):
    wait = WebDriverWait(driver, 10)

    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[.//span[text()='{button_text}']]")))
    button.click()

    option = wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//div[@role='option']//span[text()='{option_text}']/..")
    ))

    option.click()

    time.sleep(0.01)

def scrape_table_with_lazy_loading(driver, target_id=None):
    if target_id is None: return None
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    seen_row_count = 0
    max_wait_attempts = 7

    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        current_row_count = len(rows)

        if current_row_count == seen_row_count:
            max_wait_attempts -= 1
            if max_wait_attempts == 0:
                break
        else:
            max_wait_attempts = 5

        if rows:
            last_row = rows[-1]
            driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", last_row)

        time.sleep(0.3)
        seen_row_count = current_row_count

    rows = driver.find_elements(By.CSS_SELECTOR, "table tr")

    before_element = None
    target_element = None
    found = False
    after_element = None

    for i, row in enumerate(rows):
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text for cell in cells]

        if len(cells) < 2:
            continue
        elif found:
            after_element = row_data
            break
        if row_data[1] == target_id:
            target_element = row_data
            found = True
            continue
        before_element = row_data

    return before_element, target_element, after_element


def search(parameters: dict, target_id: str, web_driver=webdriver.Safari):
    # if isinstance(web_driver, webdriver.Chrome) or not web_driver:
    #     options = webdriver.ChromeOptions()
    #     options.add_argument("--headless")
    #     driver = webdriver.Chrome(options=options)
    # elif isinstance(web_driver, webdriver.Safari):
    options = SafariOptions()
    options.add_argument("--headless")
    driver = webdriver.Safari(options=options)
    # else:
    #     raise TypeError("driver must be either a selenium webdriver or a webdriver.Chrome")

    try:
        driver.get("https://my.innopolis.university/admissions-ranking")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button")))
        try:
            select_dropdown_item(driver, "Education level", parameters["education_level"])
            select_dropdown_item(driver, "Enrollment basis", parameters["enrollment_basis"])
            select_dropdown_item(driver, "Enrollment category", parameters["enrollment_category"])
            select_dropdown_item(driver, "Program", parameters["program"])
        except KeyError:
            raise KeyError("Wrong parameters")
        time.sleep(0.5)

        row_above, target_row, row_below = scrape_table_with_lazy_loading(driver, target_id=target_id)
        print("DEBUG:", target_row)

        return row_above, target_row, row_below

        # if target_row:
        #     print(f"\nНайдена строка с ID {target_id}: {target_row}")
        #
        #     if row_above:
        #         print(f"Строка выше по позиции: {row_above}")
        #     else:
        #         print("Нет строки выше (это первая строка)")
        #
        #     if row_below:
        #         print(f"Строка ниже по позиции: {row_below}")
        #     else:
        #         print("Нет строки ниже (это последняя строка)")
        # else:
        #     print(f"Строка с ID {target_id} не найдена")

    finally:
        driver.quit()


# if __name__ == "__main__":
#     main()