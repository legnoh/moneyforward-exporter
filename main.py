import os,platform,time,yaml,sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from prometheus_client import CollectorRegistry, start_http_server

import modules.moneyforward.common as mf
import modules.moneyforward.monthly as mf_monthly
import modules.moneyforward.assets as mf_assets
import modules.moneyforward.liability as mf_liability
import modules.moneyforward.budgets as mf_budgets

# initialize
print("initializing exporter...")
registry = CollectorRegistry()
start_http_server(int(os.environ.get('PORT', 8000)), registry=registry)

# initialize chromium & selenium webdriver
print("initializing chromium & selenium webdriver...")
options = webdriver.ChromeOptions()
options.add_argument('--disable-dev-shm-usage')

chromedriver_path = ChromeDriverManager().install()
if platform.system() == 'Linux':
    chromedriver_path = "/usr/bin/chromedriver"

driver = webdriver.Chrome(
    options=options,
    service=ChromiumService(executable_path=chromedriver_path)
)

with open('config/scraping.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

with open('config/metrics.yml', 'r') as stream:
    metrics = yaml.load(stream, Loader=yaml.FullLoader)

# create all metrics instances
print("create all metrics instances...")
all_metrics = mf.create_metric_all_instance(metrics, registry)

# login
print("login to moneyforward...")
username = os.environ['MONEYFORWARD_EMAIL']
password = os.environ['MONEYFORWARD_PASSWORD']
mf_driver = mf.login(driver, username, password)
if mf_driver == None:
    print("ERROR: login failed")
    sys.exit(1)

while True:

    # get Monthly balance metrics
    print("gathering monthly data...")
    mf_monthly.set_monthly_metrics(mf_driver,all_metrics,config['monthly']['balance'], metrics['monthly']['balance'])

    print("gathering withdrawal data...")
    mf_monthly.set_latest_withdrawal_metrics(mf_driver,all_metrics,config['monthly']['withdrawal'], metrics['monthly']['withdrawal'])

    # set assets metrics
    print("gathering assets data...")
    mf_assets.set_assets_metrics(mf_driver,all_metrics,config['assets'], metrics['assets'])

    # set liability metrics
    print("gathering liability data...")
    mf_liability.set_liability_metrics(mf_driver,all_metrics,config['liability'], metrics['liability'])

    # set budget metrics
    print("gathering budget data...")
    mf_budgets.set_budget_metrics(mf_driver,all_metrics,config['budget'], metrics['budget'])

    print("exporting moneyforward data successfully!")

    time.sleep(3600*4)
