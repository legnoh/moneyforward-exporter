import logging,os,time,yaml,sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from prometheus_client import CollectorRegistry, start_http_server
from pyvirtualdisplay import Display

import modules.moneyforward.common as mf
import modules.moneyforward.monthly as mf_monthly
import modules.moneyforward.assets as mf_assets
import modules.moneyforward.liability as mf_liability
import modules.moneyforward.budgets as mf_budgets

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
log_level = os.getenv("LOGLEVEL", logging.INFO)
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

if __name__ == '__main__':

    logging.info("# initializing exporter...")
    registry = CollectorRegistry()
    start_http_server(int(os.environ.get('PORT', 8000)), registry=registry)

    logging.info("# initializing chromium options...")
    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=/tmp/moneyforward-exporter/userdata')

    logging.info("# loading config files...")
    with open('config/scraping.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    with open('config/metrics.yml', 'r') as stream:
        metrics = yaml.load(stream, Loader=yaml.FullLoader)

    logging.info("# create all metrics instances...")
    all_metrics = mf.create_metric_all_instance(metrics, registry)

    while True:
        if os.path.isfile("/.dockerenv"):
            logging.info("# start display...")
            display = Display(visible=0, size=(1024, 768))
            display.start()

        logging.info("# start selenium...")
        driver = webdriver.Chrome(service=Service(), options=options)
        driver.implicitly_wait(0.5)

        logging.info("# login to moneyforward...")
        username = os.environ['MONEYFORWARD_EMAIL']
        password = os.environ['MONEYFORWARD_PASSWORD']
        driver = mf.login(driver, username, password)
        if driver == None:
            sys.exit(1)

        logging.info("# gathering monthly data...")
        mf_monthly.set_monthly_metrics(driver,all_metrics,config['monthly']['balance'], metrics['monthly']['balance'])

        logging.info("# gathering withdrawal data...")
        mf_monthly.set_latest_withdrawal_metrics(driver,all_metrics,config['monthly']['withdrawal'], metrics['monthly']['withdrawal'])

        logging.info("# gathering assets data...")
        mf_assets.set_assets_metrics(driver,all_metrics,config['assets'], metrics['assets'])

        logging.info("# gathering liability data...")
        mf_liability.set_liability_metrics(driver,all_metrics,config['liability'], metrics['liability'])

        logging.info("# gathering budget data...")
        mf_budgets.set_budget_metrics(driver,all_metrics,config['budget'], metrics['budget'])

        logging.info("# exporting moneyforward data successfully!")
        driver.quit()
        if os.path.isfile("/.dockerenv"):
            display.stop()
        time.sleep(3600*4)
