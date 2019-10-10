#!/usr/bin/python
# coding: utf8

import logging
import os
import json

from flask import Blueprint, Response, Markup, render_template_string, send_file, make_response
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


def cdn_tags_context():
    jquery = Markup('<script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>')
    jquery_ui = Markup('<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js" integrity="sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU=" crossorigin="anonymous"></script>')
    jquery_ui_css = Markup('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/themes/base/jquery-ui.min.css" integrity="sha256-sEGfrwMkIjbgTBwGLVK38BG/XwIiNC/EAG9Rzsfda6A=" crossorigin="anonymous" />')
    echarts = Markup('<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/4.3.0/echarts-en.min.js" integrity="sha256-0BLhrT+xIfvJO+8OfHf8iWMDzUmoL+lXNyswCl7ZUlY=" crossorigin="anonymous"></script>')
    return {"jquery_cdn": jquery, "jquery_ui_cdn": jquery_ui, "jquery_ui_css_cdn": jquery_ui_css, "echarts_cdn": echarts}


def render_chart(chart, div_id, template="chart.html"):
    with open(os.path.join(main_template_dir, template), 'r') as tfile:
        return Markup(render_template_string(tfile.read(), chart_instance=chart, div_id=div_id))


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
        app.context_processor(cdn_tags_context)

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

@echarts_bp.route('/echarts.css')
def echarts_css():
    return send_file(os.path.join(lib_dir, "slider", "css", "style.css"), mimetype='text/css')

@echarts_bp.route('/icons-classic/<imagename>.png')
def slider_img(imagename):
    return send_file(os.path.join(lib_dir, "slider", "css", "icons-classic", "{}.png".format(imagename)))

@echarts_bp.route('/flask_echarts.js')
def echarts_javascript():
    with open(os.path.join(lib_dir, "slider", "js", "jQDateRangeSlider.min.js"), 'r') as j_file1:
        with open(os.path.join(lib_dir, "echarts", "js", "echarts.widget.js"), 'r') as j_file2:
            full_js = j_file1.read() + "\n" + j_file2.read()
            response = make_response(full_js)
            response.headers.set('Content-Type', 'text/javascript')
            return response
