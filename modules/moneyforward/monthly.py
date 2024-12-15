import datetime, logging
import modules.moneyforward.common as mf
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

# get monthly balance data
def set_monthly_metrics(driver:WebDriver, all_metrics, config, metrics):
    driver.get(config['url'])

    logging.info("## get monthly metrics title...")
    try:
        period = driver.find_element(By.CSS_SELECTOR, config['css_selector']['title']).text.lstrip("(").rstrip(")")
    except NoSuchElementException as e:
        logging.warning("### get monthly metrics title process was failed...: %s", e.msg)
        mf.save_debug_information(driver, "get_monthly_metrics_title")
        return
    
    logging.info("## get monthly metrics datas...")
    try:
        datas = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['data'])
    except NoSuchElementException as e:
        logging.warning("### get monthly metrics title process was failed...: %s", e.msg)
        mf.save_debug_information(driver, "get_monthly_metrics_datas")
        return

    # define and set value
    i = 0
    for metric in metrics['metrics']:
        m = all_metrics[metric['name']]
        m.labels(period).set(mf.format_balance(datas[i].text))
        i += 1

# get monthly drawal data
def set_latest_withdrawal_metrics(driver:WebDriver,all_metrics,config,metrics):
    driver.get(config['url'])
    now = datetime.datetime.now()

    logging.info("## get latest withdrawal metrics datas...")
    try:
        accounts = driver.find_elements(By.CSS_SELECTOR, config['css_selector']['accounts'])
    except NoSuchElementException as e:
        logging.warning("### get latest withdrawal metrics process was failed...: %s", e.msg)
        mf.save_debug_information(driver, "get_latest_withdrawal")
        return

    m_price = None
    m_schedule = None

    for account in accounts:
        try:
            logging.info("## account: %s", account.text.split("\n")[0])
            name_raw = account.find_element(By.CSS_SELECTOR, config['css_selector']['name']).text
            updated = account.find_element(By.CSS_SELECTOR, config['css_selector']['updated']).text
            name = name_raw.replace(updated, '').replace('\n', '')

            price = mf.format_balance(account.find_element(By.CSS_SELECTOR, config['css_selector']['price']).text)
            logging.info("### price: %s", price)

            schedule_raw = mf.format_balance(account.find_element(By.CSS_SELECTOR, config['css_selector']['schedule']).text, 'str')
            schedule_dt = datetime.datetime.strptime(schedule_raw, '引き落とし日:(%Y/%m/%d)')
            schedule = schedule_dt.strftime("%Y/%m/%d")
            logging.info("### schedule: %s", schedule_dt)

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
