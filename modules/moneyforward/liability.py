import modules.moneyforward.common as mf
from selenium.webdriver.common.by import By

def set_liability_metrics(driver, all_metrics, config, metrics):
    driver.get(config['url'])

    # liability_total_jpy
    liability_total = mf.format_balance(driver.find_element(By.CSS_SELECTOR, config['total_amount']['css_selector']).text)
    total_metric = all_metrics[metrics['total']['metrics'][0]['name']]
    set_metric_liability_total(total_metric, liability_total)

    # liability_subtotal_jpy
    subtotals = mf.kv_table_to_dict(driver.find_element(By.CSS_SELECTOR, config['subtotal_amount']['css_selector']))
    subtotal_metric = all_metrics[metrics['subtotal']['metrics'][0]['name']]
    for name, value in subtotals.items():
        set_metric_liability_subtotal(subtotal_metric, name, value)

    # liability_detail_jpy
    liabilities = mf.table_to_dict(driver.find_element(By.CSS_SELECTOR, config['accounts']['css_selector']['table']))
    mf.set_metrics_by_table_data(liabilities, metrics['detail'], all_metrics)

def set_metric_liability_total(m, value):
    m.set(value)

def set_metric_liability_subtotal(m, name, value):
    m.labels(name).set(value)
