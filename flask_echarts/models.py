#!/usr/bin/python
# coding: utf8

import pendulum
from flask import request, jsonify

from collections import defaultdict

from flask import render_template_string


class BaseChart(object):
    TITLE = None
    TOOLBOX = {
        "feature": {
            "dataZoom": {
                "yAxisIndex": 'none'
            },
            "restore": {},
            "saveAsImage": {}
        },
        "show": True
    }

    def __init__(self, series, min_days=7, default_days=14, max_days=90, **kwargs):
        self.series = []
        for s in series:
            self.add_series(s)
        from .echarts import render_chart
        self.render_function = render_chart
        self._range_limits = None
        self._default_days = default_days
        self._min_days = min_days
        self._max_days = max_days

    @property
    def ID(self):
        return "someid"

    def is_data_request(self):
        if request.args.get("action") == "data":
            if request.args.get("chart_id") == self.ID:
                return True
        return False

    def get_url(self):
        return "{}?action=data&chart_id={}".format(request.path, self.ID)

    def get_value(self, name):
        if hasattr(self, name.upper()):
            return getattr(self, name.upper(), None)

    def add_series(self, s):
        self.series.append(s)

    def get_range_limits(self):
        if self._range_limits is None:
            min_dt1 = pendulum.now("utc").subtract(days=4*365)
            max_dt2 = pendulum.now("utc").add(days=1)
            d1 = None
            d2 = None
            for s in self.series:
                _d1, _d2 = s.get_range()
                if _d1:
                    if d1 is None:
                        d1 = _d1
                    else:
                        d1 = min(d1, _d1)
                if _d2:
                    if d2 is None:
                        d2 = _d2
                    else:
                        d2 = min(d2, _d2)
            self._range_limits = dict(min=d1 if d1 else min_dt1,
                                      max=d2 if d2 else max_dt2)
        return self._range_limits

    def get_iso_range_limits(self):
        l = self.get_range_limits()
        return dict(min=l["min"].isoformat(), max=l["max"].isoformat())

    def default_range(self):
        return self._default_days

    def min_range(self):
        return self._min_days

    def max_range(self):
        return self._max_days

    def get_series_def(self):
        out = []
        for s in self.series:
            out.append({
                "name": s.name,
                "type": s.series_type,
                "smooth": False,
                "showSymbol": False,
                "encode": {"x": 'timestamp', "y": s.name}
            })
        return out

    def calculate_range(self):
        limits = self.get_range_limits()
        d2 = limits["max"].end_of('day')
        d1 = d2.subtract(days=self.default_range()).start_of("day")
        if request:
            r_d1 = request.args.get("from_date", None)
            r_d2 = request.args.get("to_date", None)
            if r_d1:
                d1 = pendulum.parse(r_d1)
                d1 = d1.start_of('day')
            if r_d2:
                d2 = pendulum.parse(r_d2)
                d2 = d2.end_of('day')
        return dict(min=d1, max=d2)

    def get_dataset(self):
        series_count = len(self.series)
        series_names = []
        o = defaultdict(lambda: [0] * series_count)
        for i, s in enumerate(self.series):
            series_names.append(s.name)
            for dt, value in s._get_data(**self.calculate_range()):
                o[dt][i] = value
        source = []
        dimensions = ["timestamp"] + series_names
        for j, dim in enumerate(o):
            line = [dim] + o[dim]
            source.append(line)
        return {"source": source, "dimensions": dimensions}

    def build_options(self):
        return {
            "title": {
                "text": self.get_value("title")
            },
            "dataset": self.get_dataset(),
            "toolbox": self.get_value("toolbox"),
            "tooltip": {"trigger": 'axis'},
            "legend": {
                "type": 'scroll',
                "bottom": 5
            },
            "xAxis": {
                "type": 'time',
                "minInterval": 12 * 60 * 60 * 1000
            },
            "yAxis": {"type": "value"},
            "series": self.get_series_def()}

    def render(self):
        return self.render_function(self)

    def data(self):
        return jsonify(self.get_dataset())


class TimeSeries(object):
    def __init__(self, name, series_type="line"):
        self.name = name
        self.series_type = series_type

    def _get_data(self, min, max):
        return self.get_data(min, max)
