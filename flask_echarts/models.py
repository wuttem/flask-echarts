#!/usr/bin/python
# coding: utf8

import pendulum
from flask import request, jsonify

from collections import defaultdict

from flask import render_template_string


class BaseChart(object):
    TOOLBOX = {
        "feature": {
            "dataZoom": {
                "yAxisIndex": 'none'
            },
            "restore": {},
            "saveAsImage": {}
        },
        "show": True,
        "right": "5%"
    }

    def __init__(self, title="", series=None, min_days=7, default_days=14,
                 max_days=90, context=None, initial_data=True, theme=None, **kwargs):
        self.series = []
        self.title = title
        self.theme = theme
        if series:
            for s in series:
                self.add_series(s)
        from .echarts import render_chart
        self.render_function = render_chart
        self._range_limits = None
        self._default_days = default_days
        self._min_days = min_days
        self._max_days = max_days
        self.context = {}
        self.series_changed = False
        self.initial_data = initial_data
        if context is not None:
            self.context.update(context)

    @property
    def ID(self):
        return "someid"

    def is_post_request(self):
        if request.method == "POST":
            data = request.get_json()
            if data["action"] and data["chart_id"] == self.ID:
                self.handle_post_action(data)
                return True
        return False

    def enable_series(self, series_name):
        for s in self.series:
            if s.name == series_name:
                s.active = True

    def disable_series(self, series_name):
        for s in self.series:
            if s.name == series_name:
                s.active = False

    def handle_post_action(self, data):
        self.context.update(data)
        print(data)
        if "series" in data:
            for series_name in data["series"]:
                if data["series"][series_name]["active"]:
                    self.enable_series(series_name)
                else:
                    self.disable_series(series_name)
        print(self.active_series)

    def get_context_value(self, name, default=None):
        if name in self.context:
            return self.context[name]
        if default is not None:
            return default
        raise KeyError("context value {} not found".format(name))

    def get_url(self):
        return "{}".format(request.path)

    def get_value(self, name):
        if hasattr(self, name.upper()):
            return getattr(self, name.upper(), None)

    def add_series(self, s):
        self.series.append(s)

    @property
    def active_series(self):
        cnt = 0
        out = [s for s in self.series if s.active]
        return out[:5]

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

    def get_series_info(self):
        out = {}
        for s in self.series:
            out[s.name] = {"active": s.active, "foo": "bar"}
        return out

    def default_range(self):
        return self._default_days

    def min_range(self):
        return self._min_days

    def max_range(self):
        return self._max_days

    def get_limits(self):
        lims = self.get_iso_range_limits()
        return {
            "dt_min_iso": lims["min"],
            "dt_max_iso": lims["max"],
            "default_days": self.default_range(),
            "min_days": self.min_range(),
            "max_days": self.max_range()
        }

    def get_series_def(self):
        out = []
        for s in self.active_series:
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
        r_d1 = self.get_context_value("from_date", False)
        r_d2 = self.get_context_value("to_date", False)
        if r_d1:
            d1 = pendulum.parse(r_d1)
            d1 = d1.start_of('day')
        if r_d2:
            d2 = pendulum.parse(r_d2)
            d2 = d2.end_of('day')
        return dict(min=d1, max=d2)

    def get_dataset(self):
        series_count = len(self.active_series)
        series_names = []
        o = defaultdict(lambda: [0] * series_count)
        for i, s in enumerate(self.active_series):
            series_names.append(s.name)
            for dt, value in s._get_data(**self.calculate_range()):
                o[dt][i] = value
        source = []
        dimensions = ["timestamp"] + series_names
        for j, dim in enumerate(o):
            line = [dim] + o[dim]
            source.append(line)
        return {"source": source, "dimensions": dimensions}

    def build_options(self, with_data=True):
        return {
            "title": {
                "text": self.title,
                "left": "5%"
            },
            "useUTC": True,
            "dataset": self.get_dataset() if with_data else None,
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
            "grid": {
                "left": "5%",
                "right": "5%",
                "top": 40
            },
            "yAxis": {"type": "value"},
            "series": self.get_series_def()}

    def render(self, div_id):
        return self.render_function(self, div_id)

    def data(self):
        r = self.get_context_value("reload", False)
        out = {"reload": r}
        if r:
            print("change!!!")
            out.update(self.build_options(with_data=True))
        else:
            out["dataset"] = self.get_dataset()
        return jsonify(out)


class TimeSeries(object):
    def __init__(self, name, active=True, series_type="line"):
        self.name = name
        self.series_type = series_type
        self.active = active

    def _get_data(self, min, max):
        return self.get_data(min, max)
