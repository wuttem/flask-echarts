#!/usr/bin/python
# coding: utf8

import logging
import os
import json

from flask import Blueprint, Response, Markup, render_template_string, send_file
from flask import current_app, _app_ctx_stack


logger = logging.getLogger(__name__)
echarts_bp = Blueprint("echarts", __name__, url_prefix='/echarts')


main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
lib_dir = os.path.join(main_dir, "static")
main_template_dir = os.path.join(main_dir, "flask_echarts", "templates")


from .models import BaseChart


def json_filter():
    def my_json(s):
        return Markup(json.dumps(s))
    def my_ppjson(s):
        return Markup(json.dumps(s, indent=4, sort_keys=True))
    return {"json": my_json, "ppjson": my_ppjson}


def add_echarts_javascript(html_str):
    js = g.get("echarts_js", None)
    if js is None:
        g.echarts_js = list()
    g.echarts_js.append(html_str)
    g.echarts_js = list(set(g.add_js))


def echarts_javascript_context():
    def my_javascript():
        js = g.get("echarts_js", None)
        if js is None:
            return Markup("")
        return Markup("\n".join(js))
    return {"echarts_javascript": my_javascript}


def render_chart(chart, template="chart.html"):
    with open(os.path.join(main_template_dir, template), 'r') as tfile:
        return render_template_string(tfile.read(), chart_instance=chart)


class Echarts(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('USE_CDN', False)

        # add routes
        app.register_blueprint(echarts_bp)

        # add filters
        for n, func in json_filter().items():
            app.jinja_env.filters[n] = func
        app.context_processor(echarts_javascript_context)

        # add teardown
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        # do somthing on teardown ...

    def linechart(self, *args, **kwargs):
        return BaseChart(*args, **kwargs)


@echarts_bp.route('/echarts.min.js')
def echarts_lib_min():
    return send_file(os.path.join(lib_dir, "echarts", "js", "echarts.min.js"), mimetype='text/javascript')

@echarts_bp.route('/echarts.widget.js')
def echarts_widget():
    return send_file(os.path.join(lib_dir, "echarts", "js", "echarts.widget.js"), mimetype='text/javascript')

@echarts_bp.route('/slider.min.js')
def slider_lib_min():
    return send_file(os.path.join(lib_dir, "slider", "js", "jQDateRangeSlider.min.js"), mimetype='text/javascript')

@echarts_bp.route('/slider.css')
def slider_css():
    return send_file(os.path.join(lib_dir, "slider", "css", "style.css"), mimetype='text/css')

@echarts_bp.route('/icons-classic/<imagename>.png')
def slider_img(imagename):
    return send_file(os.path.join(lib_dir, "slider", "css", "icons-classic", "{}.png".format(imagename)))