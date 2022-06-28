import modules.moneyforward.common as mf
from selenium.webdriver.common.by import By

def set_budget_metrics(driver, registry, config, metrics):
    driver.get(config['url'])
    period = driver.find_element(By.CSS_SELECTOR, config['css_selector']['period']).text
    
    m = {}
    for genre,budget_metrics in metrics.items():
        m[genre] = {}
        for budget_key, budget_value in budget_metrics.items():
            for metric in budget_value['metrics']:
                m[genre][budget_key] = mf.create_metric_instance(metric, registry)

    budgets = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['budgets'])
    for budget in budgets:
        progress = mf.format_balance(budget.find_element(By.CSS_SELECTOR, config['css_selector']['progress']).text)
        balance = mf.format_balance(budget.find_element(By.CSS_SELECTOR, config['css_selector']['balance']).text)

        classes = budget.get_attribute('class').split()
        if config['css_selector']['total_class_name'] in classes:
            m['progress']['total'].labels(period).set(progress)
            m['balance']['total'].labels(period).set(balance)
        elif config['css_selector']['subtotal_class_name'] in classes:
            name = budget.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            m['progress']['subtotal'].labels(period, name).set(progress)
            m['balance']['subtotal'].labels(period, name).set(balance)
        else:
            name = budget.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            m['progress']['category'].labels(period, name).set(progress)
            m['balance']['category'].labels(period, name).set(balance)
