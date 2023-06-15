#!/bin/bash

# deploy Hive with Docker
printf "Deploy Hive with Docker\n"
docker-compose up -d

printf "Waiting for Hive\n"

is_healthy() {
    service="$1"
    container_id="$(docker-compose ps -q "$service")"
    health_status="$(docker inspect -f "{{.State.Health.Status}}" "$container_id")"

    if [ "$health_status" = "healthy" ]; then
        return 0
    else
        return 1
    fi
}
while ! is_healthy hive-server; do sleep 1; done

sudo chown -R $USER:$USER data

printf "=========================================================\n"

printf "FILE DOWNLOAD\n"
# list of files to download
imdb=('title.basics.tsv' 'title.ratings.tsv' 'title.principals.tsv' 'name.basics.tsv' 'title.crew.tsv' 'title.episode.tsv' 'title.akas.tsv')

# download files
for i in "${imdb[@]}"
do
  if [ ! -f data/$i ]; then
    printf "Downloading %s\n" $i
    wget -c https://datasets.imdbws.com/$i.gz -O - | gunzip > data/$i
    else printf "File %s already exists\n" $i
  fi
done

printf "=========================================================\n"
printf "Configure Python environment\n"
python3 -m venv imdb-hive

printf "=========================================================\n"
printf "Install Python dependencies\n"
source imdb-hive/bin/activate
pip3 install -r requirements.txt

printf "=========================================================\n"
printf "Create Hive tables\n"
python3 ./load_data.py


printf "=========================================================\n"
printf "Processing Movie table for more efficient partitions and buckets\n"
python3 ./process_data.py

printf "=========================================================\n"
printf "Quick queries to demonstrate usage of partitions\n"
python3 ./query_data.py


