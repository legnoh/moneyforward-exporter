moneyforward_exporter
====

## WIP

Prometheus exporter for [MoneyForward ME](https://www.moneyforward.com/).

## Usage

This exporter script works for creating metrics file only.

```sh
git clone https://github.com/legnoh/moneyforward_exporter.git && cd moneyforward_exporter
pipenv install
pipenv shell
MF_EMAIL=$YOUR_EMAIL MF_PASSWORD=$YOUR_PASSWORD pipenv run main
```

Therefore, you should be hosted in other container to export metrics.

```sh
cd container
docker-compose up -d
curl -vvv http://localhost:9101/moneyforward.prom
```

## Metrics

please check [metrics.yml](./config/metrics.yml) or [example](./container/example/moneyforward.prom)
