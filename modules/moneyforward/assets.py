import modules.moneyforward.common as mf

def set_assets_metrics(driver, registry, config, metrics):
    driver.get(config['url'])

    # assets_total_jpy
    asset_total = mf.format_balance(driver.find_element_by_css_selector(config['total_amount']['css_selector']).text)
    total_metric = mf.create_metric_instance(metrics['total']['metrics'][0], registry)
    set_metric_assets_total(total_metric, asset_total)

    # assets_subtotal_jpy, assets_*
    subtotal_metric = mf.create_metric_instance(metrics['subtotal']['metrics'][0], registry)
    for name, selector in config['genre']['css_selector'].items():

        title = driver.find_element_by_css_selector(selector['root'] + selector['title']).text
        amount = mf.format_balance(driver.find_element_by_css_selector(selector['root'] + selector['amount']).text)
        accounts = mf.table_to_dict(driver.find_element_by_css_selector(selector['root'] + selector['table']))

        set_metric_assets_subtotal(subtotal_metric, title, amount)
        mf.set_metrics_by_table_data(accounts, metrics[name], registry)

def set_metric_assets_total(m, value):
    m.set(value)

def set_metric_assets_subtotal(m, name, value):
    m.labels(name).set(value)
