import logging
import modules.moneyforward.common as mf
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def set_liability_metrics(driver, all_metrics, config, metrics):
    driver.get(config['url'])

    # liability_total_jpy
    logging.info("## gathering liability total...")
    try: 
        liability_total = mf.format_balance(driver.find_element(By.CSS_SELECTOR, config['total_amount']['css_selector']).text)
        total_metric = all_metrics[metrics['total']['metrics'][0]['name']]
        set_metric_liability_total(total_metric, liability_total)
    except NoSuchElementException as e:
        logging.warning("### get total liability total process was failed...: %s", e.msg)

    # liability_subtotal_jpy
    logging.info("## gathering liability subtotal...")
    try:
        subtotals = mf.kv_table_to_dict(driver.find_element(By.CSS_SELECTOR, config['subtotal_amount']['css_selector']))
        subtotal_metric = all_metrics[metrics['subtotal']['metrics'][0]['name']]
        for name, value in subtotals.items():
            set_metric_liability_subtotal(subtotal_metric, name, value)
    except NoSuchElementException as e:
        logging.warning("### get total liability subtotal process was failed...: %s", e.msg)

    # liability_detail_jpy
    logging.info("## gathering liability details...")
    try:
        liabilities = mf.table_to_dict(driver.find_element(By.CSS_SELECTOR, config['accounts']['css_selector']['table']))
        mf.set_metrics_by_table_data(liabilities, metrics['detail'], all_metrics)
    except NoSuchElementException as e:
        logging.warning("### get total liability detail process was failed...: %s", e.msg)

def set_metric_liability_total(m, value):
    m.set(value)

def set_metric_liability_subtotal(m, name, value):
    m.labels(name).set(value)
