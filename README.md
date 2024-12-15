moneyforward-exporter
====

Prometheus exporter for [MoneyForward ME](https://www.moneyforward.com/).

## Usage

### docker

```sh
# please fulfil your credentials
cat <<EOF > .env
MONEYFORWARD_EMAIL=youremail@localhost
MONEYFORWARD_PASSWORD=yourawesomepassword
EOF

# start
docker run -d -p 8000:8000 \
  --env-file .env \
  legnoh/moneyforward-exporter

# option: start with debugdir mount
mkdir -p $HOME/moneyforward-exporter
docker run -d -p 8000:8000 \
  --env-file .env \
  -v $HOME/moneyforward-exporter:/tmp/moneyforward-exporter \
  legnoh/moneyforward-exporter

# wait 60s and get request
curl http://localhost:8000/metrics
```

### local

```sh
# clone
git clone https://github.com/legnoh/moneyforward-exporter.git && cd moneyforward-exporter
pipenv install

# please fulfil your credentials
cp example.env .env
vi .env

# execute
pipenv run main
```

## Metrics

please check [example](./example.prom)

## Disclaim / 免責事項

- 当スクリプトは、MoneyForward 本家からは非公認のものです。
  - これらを利用したことによるいかなる損害についても当方では責任を負いかねます。
- 当スクリプトはこれらのサイトに対し、負荷をかけることを目的として制作したものではありません。
  - 利用の際は常識的な範囲でのアクセス頻度に抑えてください。
- 先方に迷惑をかけない範囲での利用を強く推奨します。
