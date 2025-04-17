set -ex
docker-compose up -d
sleep 10
pytest . 1> log.log 2>error.log
