import os
import yaml
from selenium import webdriver
import chromedriver_binary
import modules.moneyforward.common as mf
import modules.moneyforward.monthly as mf_monthly
import modules.moneyforward.assets as mf_assets
import modules.moneyforward.liability as mf_liability
from prometheus_client import CollectorRegistry, write_to_textfile

# initialize
registry = CollectorRegistry()
driver = webdriver.Chrome()

with open('config/scraping.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

with open('config/metrics.yml', 'r') as stream:
    metrics = yaml.load(stream, Loader=yaml.FullLoader)

# login
mf_driver = mf.login(driver, os.environ['MF_EMAIL'], os.environ['MF_PASSWORD'])

# get Monthly balance metrics
print("gathering monthly data...")
mf_monthly.set_monthly_metrics(mf_driver,registry,config['monthly'], metrics['monthly'])

# set assets metrics
print("gathering assets data...")
mf_assets.set_assets_metrics(mf_driver,registry,config['assets'], metrics['assets'])

# set liability metrics
print("gathering liability data...")
mf_liability.set_liability_metrics(mf_driver,registry,config['liability'], metrics['liability'])

mf_driver.quit()
write_to_textfile('./container/public/moneyforward.prom', registry)
print("scraping account is successfull!")
