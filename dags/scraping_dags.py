from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models.baseoperator import chain
from docker.types import Mount

# docker compose build --no-cache
# docker compose up -d

# Si Airflow corre EN Docker y quieres usar su red:
network_mode="airflow_net"
# Si Airflow corre FUERA de Docker (instalación nativa), omite network_mode.

default_args = {
    'owner': 'airflow',
    'retries': 1,
    # 'retries': 5,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'scraping_main_run',
    start_date = datetime(2025, 8, 18),
    default_args=default_args,
    schedule_interval='@weekly',
    catchup=False,
    tags=["scrapy", "seleniumbase", "captcha_solver"],
) as dag:

    # run_scraping = BashOperator(
    #     task_id='run_scraping_script',
    #     bash_command='cd /opt/airflow/tesis-scraping && source venv/bin/activate && python extraccion/main.py'

    # )
    scrape_prods_vars = DockerOperator(
        task_id="scrape_prods_vars",
        image="spi_scraper:latest",
        api_version="auto",
        auto_remove=True,
        mem_limit="4g",        # más RAM para Chrome
        shm_size="2g",         # /dev/shm grande: evita crashes de Chrome
        command=["python", "extraccion/main.py"],
        docker_url="unix://var/run/docker.sock",
        network_mode="airflow_net",  # si usas la red compartida
        environment={
            "FLARESOLVERR_URL": "http://flaresolverr:8191",
            "MONGO_URI": "mongodb://host.docker.internal:27017/bodies_scraping",
            "SB_HEADLESS": "1",
            "SB_ARGS": "--no-sandbox --disable-dev-shm-usage --disable-gpu --window-size=1920,1080",
        },
        mount_tmp_dir=False,
        extra_hosts={"host.docker.internal": "host-gateway"},
        # monta si quieres que los datos salgan al host
        mounts=[
            Mount(
                source="/Users/sage/Documents/spiView/Tesis-Scraping/dataset",
                target="/app/dataset",
                type="bind",
            ),
            Mount(
                source="/Users/sage/Documents/spiView/Tesis-Scraping/extraccion/dataset",
                target="/app/extraccion/dataset",
                type="bind",
            ),
            # Optional:
            # Mount(
            #     source="/Users/sage/Documents/spiView/Tesis-Scraping/data",
            #     target="/app/data",
            #     type="bind",
            # ),
        ],
    )
