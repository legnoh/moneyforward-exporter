import time
from prometheus_client import Gauge, Counter, Info
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def login(driver, email, password):
    try:
        driver.get('https://id.moneyforward.com/sign_in/')

        # メール入力
        email_box = driver.find_element(By.NAME, 'mfid_user[email]')
        email_box.send_keys(email)
        email_box.submit()

        # パスワード入力
        password_box = driver.find_element(By.NAME, 'mfid_user[password]')
        password_box.send_keys(password)
        password_box.submit()

        # このアカウントでログインするの画面を通る
        driver.get('https://moneyforward.com/sign_in/')
        driver.find_element(By.ID, 'submitto').click()

        # バイオメトリクス認証の画面が出ていた場合は後で登録を押す
        if str(driver.current_url).startswith("https://id.moneyforward.com/passkey_promotion"):
            driver.find_element(By.CSS_SELECTOR, "main.js-mfid-users-passkey-promotions-show > div > div > div > div > section > div > a").click()

        time.sleep(10)
        return driver

    except NoSuchElementException:
        return None

def reload(driver):
    driver.get('https://moneyforward.com/');
    refresh_button = driver.find_element(By.CSS_SELECTOR, 'a.refresh')
    refresh_button.click()
    time.sleep(300)
    driver.refresh()
    return driver

def judge_column_type(column_name):
    if column_name == '残高':
        return 'int'
    elif column_name == '保有数':
        return 'int'
    elif column_name == '平均取得単価':
        return 'int'
    elif column_name == '基準価額':
        return 'int'
    elif column_name == '評価額':
        return 'int'
    elif column_name == '前日比':
        return 'int'
    elif column_name == '評価損益':
        return 'int'
    elif column_name == '評価損益率':
        return 'float'
    elif column_name == '取得価額':
        return 'int'
    elif column_name == '現在価値':
        return 'int'
    elif column_name == 'ポイント・マイル数':
        return 'int'
    elif column_name == '換算レート':
        return 'float'
    elif column_name == '現在の価値':
        return 'int'
    elif column_name == None:
        return 'int'
    else:
        return 'str'

def format_balance(string_price, key_name=None):
    column_type = judge_column_type(key_name)
    string_price = string_price.strip()

    if column_type != 'str':
        needles = ['資産総額', '負債総額', '合計', ':', '：', ',', '円', 'ポイント', '%', 'マイル', '当月利用額', '未確定', '引き落とし日', '当月分締め日', '(', ')', ' ', '　', '\n']
        for needle in needles:
            string_price = string_price.replace(needle, '')

    if column_type == 'int':
        if string_price == '':
            return 0
        elif string_price == '-':
            return 0
        return int(string_price)
    elif column_type == 'float':
        if string_price == '':
            return 0.0
        elif string_price == '-':
            return 0.0
        return float(string_price)
    else:
        return string_price

def table_to_dict(table):
    results = []
    rows = table.find_elements(By.TAG_NAME, 'tr')
    keys = rows[0].find_elements(By.TAG_NAME, 'th')
    rows.pop(0)
    
    for tr in rows:
        account = tr.find_elements(By.TAG_NAME, 'td')
        result = {}
        for i in range(len(keys)):
            result[keys[i].text] = format_balance(account[i].text, keys[i].text)
        results.append(result)
    return results

def kv_table_to_dict(table):
    result = {}
    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        key = row.find_element(By.TAG_NAME, 'th').text
        price = row.find_element(By.TAG_NAME, 'td').text
        result[key] = format_balance(price)
    return result

def create_metric_instance(metric, registry):
    if metric['type'] == 'gauge':
        m = Gauge(metric['name'], metric['desc'], metric['labels'], registry=registry)
    elif metric['type'] == 'counter':
        m = Counter(metric['name'], metric['desc'], metric['labels'], registry=registry)
    elif metric['type'] == 'summary':
        m = Counter(metric['name'], metric['desc'], metric['labels'], registry=registry)
    elif metric['type'] == 'info':
        m = Info(metric['name'], metric['desc'], metric['labels'], registry=registry)
    else:
        return None
    return m

def create_metric_all_instance(metrics:dict, registry):
    all_metrics ={}
    for main_category in metrics.values():
        for sub_category in main_category.values():
           for single_metrics in sub_category['metrics']:
               m = create_metric_instance(single_metrics, registry)
               all_metrics[single_metrics['name']] = m
    return all_metrics

def set_metrics_by_table_data(accounts, metrics, all_metrics):
    for metric in metrics['metrics']:
        m = all_metrics[metric['name']]
        for account in accounts:
            labels = []
            for label in metrics['labels']['value']:
                labels.append(account[label])
            if m is None:
                continue
            elif m._type == 'gauge':
                m.labels(*labels).set(account[metric['th']])
            elif m._type == 'info':
                infos = {}
                for info in metric['values']:
                    infos[info['key']] = account[info['th']]
                m.labels(*labels).info(infos)
            elif m._type == 'counter':
                m.labels(*labels).inc(account[metric['th']])
