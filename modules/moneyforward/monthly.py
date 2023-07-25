import modules.moneyforward.common as mf
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# get monthly balance data
def set_monthly_metrics(driver, all_metrics, config, metrics):
    driver.get(config['url'])

    period = driver.find_element(By.CSS_SELECTOR, config['css_selector']['title']).text.lstrip("(").rstrip(")")
    datas = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['data'])

    # define and set value
    i = 0
    for metric in metrics['metrics']:
        m = all_metrics[metric['name']]
        m.labels(period).set(mf.format_balance(datas[i].text))
        i += 1

# get monthly drawal data
def set_latest_withdrawal_metrics(driver,all_metrics,config,metrics):
    driver.get(config['url'])

    accounts = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['accounts'])
    m_price = None
    m_schedule = None

    for account in accounts:
        try:
            name_raw = account.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            updated = account.find_element(By.CSS_SELECTOR, config['css_selector']['updated']).text
            name = name_raw.replace(updated, '').replace('\n', '')
            price = mf.format_balance(account.find_element(By.CSS_SELECTOR, config['css_selector']['price']).text)
            schedule = mf.format_balance(account.find_element(By.CSS_SELECTOR, config['css_selector']['schedule']).text, 'str')
            
            if m_price == None:
                m_price = all_metrics[metrics['metrics'][0]['name']]
            if m_schedule == None:
                m_schedule = all_metrics[metrics['metrics'][1]['name']]
            
            m_price.labels(name).set(price)
            m_schedule.labels(name).info({'schedule': schedule})
        except NoSuchElementException:
            continue
