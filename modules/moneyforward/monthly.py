import datetime, time
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

    now = datetime.datetime.now()

    accounts = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['accounts'])
    m_price = None
    m_schedule = None

    for account in accounts:
        try:
            name_raw = account.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            updated = account.find_element(By.CSS_SELECTOR, config['css_selector']['updated']).text
            name = name_raw.replace(updated, '').replace('\n', '')
            price = mf.format_balance(account.find_element(By.CSS_SELECTOR, config['css_selector']['price']).text)
            schedule_raw = mf.format_balance(account.find_element(By.CSS_SELECTOR, config['css_selector']['schedule']).text, 'str')
            schedule_dt = datetime.datetime.strptime(schedule_raw, '引き落とし日:(%Y/%m/%d)')
            schedule = schedule_dt.strftime("%Y/%m/%d")

            if m_price == None:
                m_price = all_metrics[metrics['metrics'][0]['name']]
            if m_schedule == None:
                m_schedule = all_metrics[metrics['metrics'][1]['name']]
            
            # 今日より後の場合に限り予定として表示、そうでない場合は0にする
            if (now - schedule_dt).days < 0:
                m_price.labels(name).set(price)
                m_schedule.labels(name).info({'schedule': schedule})
            else:
                m_price.labels(name).set(0)
                m_schedule.labels(name).info({'schedule': schedule})
        except NoSuchElementException:
            continue
