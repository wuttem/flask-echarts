#!/usr/bin/python
# coding: utf8

import pendulum
import random

from flask import Flask
from flask_echarts import Echarts, TimeSeries


e = Echarts()
app = Flask(__name__)
e.init_app(app)


class MySeries(TimeSeries):
    def get_range(self):
        d1 = pendulum.now("utc").subtract(days=300)
        d2 = pendulum.now("utc")
        return (d1, d2)

    def get_data(self, dt_from, dt_to):
        out = []
        cur = dt_from.replace(microsecond=0)
        while cur < dt_to:
            val = ((cur.int_timestamp / 3600) % 24) + random.random() * 10
            out.append((cur.isoformat(), val))
            cur = cur.add(minutes=10)
        return out


@app.route('/', methods=['POST', 'GET'])
def home():
    data = [MySeries("temp"), MySeries("act"), MySeries("ph", active=False)]
    linechart = e.linechart("MY Chart", series=data)
    if linechart.is_post_request():
        return linechart.data()
    return linechart.render()
