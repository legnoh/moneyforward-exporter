import modules.moneyforward.common as mf
from selenium.webdriver.common.by import By

def set_budget_metrics(driver, all_metrics, config, metrics):
    driver.get(config['url'])
    
    period = driver.find_element(By.CSS_SELECTOR, config['css_selector']['period']).text
    budgets = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['budgets'])

    for budget in budgets:
        progress = mf.format_balance(budget.find_element(By.CSS_SELECTOR, config['css_selector']['progress']).text)
        balance = mf.format_balance(budget.find_element(By.CSS_SELECTOR, config['css_selector']['balance']).text)

        classes = budget.get_attribute('class').split()
        if config['css_selector']['total_class_name'] in classes:
            all_metrics['mf_budget_progress_total_jpy'].labels(period).set(progress)
            all_metrics['mf_budget_balance_total_jpy'].labels(period).set(balance)
        elif config['css_selector']['subtotal_class_name'] in classes:
            name = budget.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            all_metrics['mf_budget_progress_subtotal_jpy'].labels(period, name).set(progress)
            all_metrics['mf_budget_balance_subtotal_jpy'].labels(period, name).set(balance)
        else:
            name = budget.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            all_metrics['mf_budget_progress_category_jpy'].labels(period, name).set(progress)
            all_metrics['mf_budget_balance_category_jpy'].labels(period, name).set(balance)

