import modules.moneyforward.common as mf

def set_liability_metrics(driver, registry, config, metrics):
    driver.get(config['url'])

    # liability_total_jpy
    liability_total = mf.format_balance(driver.find_element_by_css_selector(config['total_amount']['css_selector']).text)
    total_metric = mf.create_metric_instance(metrics['total']['metrics'][0], registry)
    set_metric_liability_total(total_metric, liability_total)

    # liability_subtotal_jpy
    subtotals = mf.kv_table_to_dict(driver.find_element_by_css_selector(config['subtotal_amount']['css_selector']))
    subtotal_metric = mf.create_metric_instance(metrics['subtotal']['metrics'][0], registry)
    for name, value in subtotals.items():
        set_metric_liability_subtotal(subtotal_metric, name, value)

    # liability_detail_jpy
    liabilities = mf.table_to_dict(driver.find_element_by_css_selector(config['accounts']['css_selector']['table']))
    mf.set_metrics_by_table_data(liabilities, metrics['detail'], registry)

def set_metric_liability_total(m, value):
    m.set(value)

def set_metric_liability_subtotal(m, name, value):
    m.labels(name).set(value)
