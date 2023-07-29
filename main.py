import logging,os,platform,time,yaml,sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.chrome.service import Service as ChromeService
from prometheus_client import CollectorRegistry, start_http_server

import modules.moneyforward.common as mf
import modules.moneyforward.monthly as mf_monthly
import modules.moneyforward.assets as mf_assets
import modules.moneyforward.liability as mf_liability
import modules.moneyforward.budgets as mf_budgets

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
log_level = os.getenv("LOGLEVEL", logging.INFO)
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

if __name__ == '__main__':

    logging.info("initializing exporter...")
    registry = CollectorRegistry()
    start_http_server(int(os.environ.get('PORT', 8000)), registry=registry)

    logging.info("initializing chromium options...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-dev-shm-usage')

    if platform.system() == 'Linux':
        logging.info("initializing chromium...")
        driver = webdriver.Chrome(service=ChromiumService(), options=options)
    else:
        logging.info("initializing chrome...")
        driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.implicitly_wait(5)

    logging.info("loading config files...")
    with open('config/scraping.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    with open('config/metrics.yml', 'r') as stream:
        metrics = yaml.load(stream, Loader=yaml.FullLoader)

    logging.info("create all metrics instances...")
    all_metrics = mf.create_metric_all_instance(metrics, registry)

    logging.info("login to moneyforward...")
    username = os.environ['MONEYFORWARD_EMAIL']
    password = os.environ['MONEYFORWARD_PASSWORD']
    mf_driver = mf.login(driver, username, password)
    if mf_driver == None:
        logging.fatal("login failed")
        sys.exit(1)

    while True:

        # get Monthly balance metrics
        logging.info("gathering monthly data...")
        mf_monthly.set_monthly_metrics(mf_driver,all_metrics,config['monthly']['balance'], metrics['monthly']['balance'])

        logging.info("gathering withdrawal data...")
        mf_monthly.set_latest_withdrawal_metrics(mf_driver,all_metrics,config['monthly']['withdrawal'], metrics['monthly']['withdrawal'])

        # set assets metrics
        logging.info("gathering assets data...")
        mf_assets.set_assets_metrics(mf_driver,all_metrics,config['assets'], metrics['assets'])

        # set liability metrics
        logging.info("gathering liability data...")
        mf_liability.set_liability_metrics(mf_driver,all_metrics,config['liability'], metrics['liability'])

        # set budget metrics
        logging.info("gathering budget data...")
        mf_budgets.set_budget_metrics(mf_driver,all_metrics,config['budget'], metrics['budget'])

        logging.info("exporting moneyforward data successfully!")
        time.sleep(3600*4)
