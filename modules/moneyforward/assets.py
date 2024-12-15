import logging
import modules.moneyforward.common as mf
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

def set_assets_metrics(driver:WebDriver, all_metrics, config, metrics):
    driver.get(config['url'])

    # assets_total_jpy
    logging.info("## asset total gathering...")
    try:
        asset_total = mf.format_balance(driver.find_element(By.CSS_SELECTOR, config['total_amount']['css_selector']).text)
        total_metric = all_metrics[metrics['total']['metrics'][0]['name']]
        set_metric_assets_total(total_metric, asset_total)
    except NoSuchElementException as e:
        logging.warning("### get total asset process was failed...: %s", e.msg)

    # assets_subtotal_jpy, assets_*
    subtotal_metric = all_metrics[metrics['subtotal']['metrics'][0]['name']]
    for name, selector in config['genre']['css_selector'].items():

        logging.info("## asset subtotal gathering...: %s", name)
        try:
            title = driver.find_element(By.CSS_SELECTOR, selector['root'] + selector['title']).text
            amount = mf.format_balance(driver.find_element(By.CSS_SELECTOR, selector['root'] + selector['amount']).text)
            accounts = mf.table_to_dict(driver.find_element(By.CSS_SELECTOR, selector['root'] + selector['table']))

            set_metric_assets_subtotal(subtotal_metric, title, amount)
            mf.set_metrics_by_table_data(accounts, metrics[name], all_metrics)

        except NoSuchElementException as e:
            continue

def set_metric_assets_total(m, value):
    m.set(value)

def set_metric_assets_subtotal(m, name, value):
    m.labels(name).set(value)
