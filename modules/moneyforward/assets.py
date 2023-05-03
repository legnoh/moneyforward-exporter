import modules.moneyforward.common as mf
from selenium.webdriver.common.by import By

def set_assets_metrics(driver, all_metrics, config, metrics):
    driver.get(config['url'])

    # assets_total_jpy
    asset_total = mf.format_balance(driver.find_element(By.CSS_SELECTOR, config['total_amount']['css_selector']).text)
    total_metric = all_metrics[metrics['total']['metrics'][0]['name']]
    set_metric_assets_total(total_metric, asset_total)

    # assets_subtotal_jpy, assets_*
    subtotal_metric = all_metrics[metrics['subtotal']['metrics'][0]['name']]
    for name, selector in config['genre']['css_selector'].items():

        title = driver.find_element(By.CSS_SELECTOR, selector['root'] + selector['title']).text
        amount = mf.format_balance(driver.find_element(By.CSS_SELECTOR, selector['root'] + selector['amount']).text)
        accounts = mf.table_to_dict(driver.find_element(By.CSS_SELECTOR, selector['root'] + selector['table']))

        set_metric_assets_subtotal(subtotal_metric, title, amount)
        mf.set_metrics_by_table_data(accounts, metrics[name], all_metrics)

def set_metric_assets_total(m, value):
    m.set(value)

def set_metric_assets_subtotal(m, name, value):
    m.labels(name).set(value)
