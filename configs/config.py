FLARESOLVERR_URL = "http://flaresolverr:8191"
MONGO_URI = "mongodb://root:example@mongodb:27017/bodies_scraping"

# Volumes (host_path:container_path)
VOLUMES = [
    "./data:/app/data",
    "./dataset:/app/dataset",
]

# Image to use
SCRAPER_IMAGE = "spi_scraper:latest"

# Entrypoint
ENTRYPOINT = "with-xvfb"
