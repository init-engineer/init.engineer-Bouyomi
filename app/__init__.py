# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/05

from flask import Flask
from .utils import chart
from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    chart.Chart

    from .main import main as main_blueprint
    from .subscribe import subscribe as subscribe_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(subscribe_blueprint)

    return app
