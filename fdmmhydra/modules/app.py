import json
import logging
import os
import shutil
import time
import traceback
import threading
from copy import deepcopy
from importlib.machinery import SourceFileLoader 
from importlib.util import module_from_spec, spec_from_loader

import subprocess

import docker
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS


def apply_env(path, env:dict, recursions=10):
  # Applies environment variables to a file
  with open(path) as f:
    contents = f.read()
  for _ in range(recursions):
    for k, v in env.items():
      contents = contents.replace(f"${k}",v).replace("${"+f"{k}"+"}",v)
  with open(path, "w+") as f:
    f.write( contents)

def load_env(path:str)->dict:
    spec = spec_from_loader("env", SourceFileLoader("env", os.path.abspath(path)))
    spec.loader.exec_module(env := module_from_spec(spec))
    env = {k:v for k,v in env.__dict__.items() if k==k.upper()}
    return env

def load_yaml(path:str)->dict:
    try:
        with open(path, 'r') as stream:
            conf = yaml.safe_load(stream)
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError(f"Error loading yaml - {e}")
    return conf

def check_container_up(container: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", container],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip()) > 0

    
# global_env = load_env("/cloudarr-home/.env")
# DOMAINNAME = global_env["DOMAINNAME"]


# class HomePageManager:
#     def __init__(self, app) -> None:
#         self.app = app

class App(Flask):
    def __init__(self, *args, **kwargs):
        Flask.__init__(self, __name__, *args, **kwargs)
        self.scheduler = BackgroundScheduler()
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def run(self):
        self.scheduler.start()
        Flask.run(self)


CORS(app)
# manager = HomePageManager(app)


def parse_headers(headers:dict) -> dict:
    groups = headers.get("Remote-Groups", "")
    if len(groups):
        groups = groups.split(",")
    if len(groups) == 1 and groups[0] == "":
        groups = []
    return {
        "user": headers.get("Remote-User", ""),
        "groups": groups
    }

@app.route('/')
@app.route('/homepage')
def index():
    return "Stuff goes here"

if __name__ == '__main__':
    logging.info("Starting")
    scheduler.start()
    app.run(host='0.0.0.0', port=8000)