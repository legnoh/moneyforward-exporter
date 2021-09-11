import modules.moneyforward.common as mf
from prometheus_client import CollectorRegistry, Gauge, write_to_textfile

def set_monthly_metrics(driver, registry, config, metrics):
    period = driver.find_element_by_css_selector(config['balance']['css_selector']['title']).text.lstrip("(").rstrip(")")
    datas = driver.find_elements_by_css_selector(config['balance']['css_selector']['data'])

    # define and set value
    i = 0
    for metric in metrics['balance']['metrics']:
        m = mf.create_metric_instance(metric, registry)
        m.labels(period).set(mf.format_balance(datas[i].text))
        i += 1
