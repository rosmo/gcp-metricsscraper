# GCP Metrics list as JSON scraper

A simple script to scrape the web page for all Google Cloud monitoring metrics and output it as JSON.

Usage:

```sh
python3.10 metricsscraper.py --pretty https://cloud.google.com/monitoring/api/metrics_gcp > metrics.json
```