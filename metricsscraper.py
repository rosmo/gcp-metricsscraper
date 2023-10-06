#!/usr/bin/env python3
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
from bs4 import BeautifulSoup
import urllib.request
import json

def scrape_metrics(url):
    metrics = {}
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html)

        for header in soup.find_all("h3"):
            if "data-text" in header.attrs:
                metrics_list = []
                metrics_table = header.find_next("tbody")
                if metrics_table:
                    i = 0
                    m = {}
                    for metric in metrics_table.find_all("tr"):
                        if "met_type" in metric["class"]:
                            c = metric.find("td")
                            metric_id = c.find("code").get_text()
                            metric_state = c.find("sup").get_text()
                            metric_description = ""
                            after_sup = False
                            for item in c.contents:
                                if item.name == "sup":
                                    after_sup = True
                                elif after_sup and isinstance(item, str):
                                    metric_description += item
                            m["id"] = metric_id
                            m["state"] = metric_state
                            m["short_desc"] = metric_description.strip()
                        if "met_desc" in metric["class"]:
                            c = metric.find("td")
                            ti = 0
                            for item in c.find_all("code"):
                                if ti == 0:
                                    m["kind"] = item.get_text()
                                elif ti == 1:
                                    m["type"] = item.get_text()
                                else:
                                    m["unit"] = item.get_text()
                                ti += 1
                            if c.find("b"):
                                m["resources"] = c.find("b").get_text()
                            else:
                                m["resources"] = ""
                            c = c.find_next("td")
                            latency = c.find("i")
                            if latency:
                                m["latency"] = latency.get_text()
                                latency.clear()
                            m["long_desc"] = c.get_text().strip()
                            metrics_list.append(m)
                            m = {}
                    metrics[header["data-text"]] = metrics_list
    return metrics         

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to scrape", default="https://cloud.google.com/monitoring/api/metrics_gcp")
    parser.add_argument("--pretty", help="Pretty print JSON", action="store_const", const=True)
    args = parser.parse_args()
    metrics = scrape_metrics(args.url)
    if args.pretty:
        print(json.dumps(metrics, indent=2))
    else:
        print(json.dumps(metrics))