import datetime, logging, time, base64, os, pyotp
from prometheus_client import Gauge, Counter, Info
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

def login(driver:WebDriver, email:str, password:str, totp_secret:str) -> WebDriver | None:
    try:
        logging.info("## jump to sign_in page...")
        driver.get('https://id.moneyforward.com/sign_in/')

        # sign_inページのURLからリダイレクトされる場合、既にログイン済なのでそのまま返す
        if '/sign_in' not in driver.current_url:
            logging.info("## already logged in")
            return driver

        # メール入力
        email_box = driver.find_element(By.NAME, 'mfid_user[email]')
        email_box.clear()
        email_box.send_keys(email)
        email_box.submit()

        # パスワード入力
        password_box = driver.find_element(By.NAME, 'mfid_user[password]')
        password_box.send_keys(password)
        password_box.submit()

        # 二要素認証のメール画面になった場合は異常終了
        if str(driver.current_url).startswith("https://id.moneyforward.com/email_otp"):
            logging.fatal("## email otp page detected! Please set up your 2FA setting in moneyforward.com!")
        
        # 通常のGoogleOTPにいけた場合は、OTPコードを入力してsubmitする
        if str(driver.current_url).startswith("https://id.moneyforward.com/two_factor_auth/totp"):
            logging.info("## totp page detected")
            # OTPコードを入力してsubmitする
            totp = pyotp.TOTP(s=totp_secret,name=email, issuer="MoneyForward")
            totp_code = totp.now()
            totp_box = driver.find_element(By.CSS_SELECTOR, 'input#otp_attempt')
            totp_box.send_keys(totp_code)
            totp_box.submit()

        # このアカウントでログインするの画面を通る
        driver.get('https://moneyforward.com/sign_in/')
        driver.find_element(By.CSS_SELECTOR, 'form > button').click()
        time.sleep(5)

        # バイオメトリクス認証の画面が出ていた場合は後で登録を押す
        if str(driver.current_url).startswith("https://id.moneyforward.com/passkey_promotion"):
            logging.info("## passkey_promotion page detected")
            driver.find_element(By.CSS_SELECTOR, "main.js-mfid-users-passkey-promotions-show > div > div > div > div > section > div > a").click()

        logging.info("## login check successfully")
        return driver

    except NoSuchElementException as e:
        logging.error("## login failed with selenium error: %s", e.msg)
        save_debug_information(driver, "login")
        return None

def update_account(driver:WebDriver) -> None:
    driver.get('https://moneyforward.com/');
    refresh_button = driver.find_element(By.CSS_SELECTOR, 'a.refresh')
    refresh_button.click()
    time.sleep(300)
    driver.refresh()

def judge_column_type(column_name) -> str:
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

def format_balance(string_price, key_name=None) -> int | float | str:
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

def table_to_dict(table) -> list[dict]:
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

def create_metric_all_instance(metrics:dict, registry) -> dict:
    all_metrics ={}
    for main_category in metrics.values():
        for sub_category in main_category.values():
           for single_metrics in sub_category['metrics']:
               m = create_metric_instance(single_metrics, registry)
               all_metrics[single_metrics['name']] = m
    return all_metrics

def set_metrics_by_table_data(accounts, metrics, all_metrics) -> None:
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

def save_debug_information(driver:WebDriver, error_slug: str) -> None:

    issuetitle = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + error_slug
    debugfile_dir = os.getenv("DEBUGFILE_DIR", "/tmp/moneyforward-exporter")

    if not os.path.exists(debugfile_dir):
        os.makedirs(debugfile_dir)

    # save sourcecode
    sourcecode = driver.execute_script("return document.body.innerHTML;")
    sourcecode_path = debugfile_dir + "/" + issuetitle + ".html"
    with open(sourcecode_path, "w") as f:
        f.write(sourcecode)
    logging.info("### sourcecode: %s", sourcecode_path)

    # save screenshot
    screenshot_data = base64.urlsafe_b64decode(driver.execute_cdp_cmd("Page.captureScreenshot", {"captureBeyondViewport": True})["data"])
    screenshot_path = debugfile_dir + "/" + issuetitle + ".png"
    with open(screenshot_path, "wb") as f:
        f.write(screenshot_data)
    logging.info("### screenshot: %s", screenshot_path)
