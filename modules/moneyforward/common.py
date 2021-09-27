import time
from prometheus_client import CollectorRegistry, Gauge, write_to_textfile, Counter, Info

def login(driver, email, password):
    driver.get('https://id.moneyforward.com/sign_in/email/');
    driver.implicitly_wait(10);
    email_box = driver.find_element_by_name('mfid_user[email]')
    email_box.send_keys(email)
    email_box.submit()

    password_box = driver.find_element_by_name('mfid_user[password]')
    password_box.send_keys(password)
    password_box.submit()

    driver.get('https://moneyforward.com/sign_in/')
    driver.find_element_by_class_name('submitBtn').click()
    return driver

def reload(driver):
    driver.get('https://moneyforward.com/');
    driver.implicitly_wait(10);
    refresh_button = driver.find_element_by_css_selector('a.refresh')
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
    string_price = string_price.strip()
    needles = ['資産総額', '負債総額', '合計', ':', '：', ',', '円', 'ポイント', '%', 'マイル', '当月利用額', '未確定', '引き落とし日', '当月分締め日', '(', ')', ' ', '　', '\n']
    for needle in needles:
        string_price = string_price.replace(needle, '')
    column_type = judge_column_type(key_name)
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
    rows = table.find_elements_by_tag_name('tr')
    keys = rows[0].find_elements_by_tag_name('th')
    rows.pop(0)
    
    for tr in rows:
        account = tr.find_elements_by_tag_name('td')
        result = {}
        for i in range(len(keys)):
            result[keys[i].text] = format_balance(account[i].text, keys[i].text)
        results.append(result)
    return results

def kv_table_to_dict(table):
    result = {}
    rows = table.find_elements_by_tag_name('tr')
    for row in rows:
        key = row.find_element_by_tag_name('th').text
        price = row.find_element_by_tag_name('td').text
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

def set_metrics_by_table_data(accounts, metrics, registry):
    for metric in metrics['metrics']:
        m = create_metric_instance(metric, registry)
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
