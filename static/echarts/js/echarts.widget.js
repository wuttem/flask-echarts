function uniqId() {
    return Math.round(new Date().getTime() + (Math.random() * 100));
}

function timeAsUTCDate(dt) {
  var d = new Date(dt)
  var utc_ts = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours(),
                        d.getMinutes(), d.getSeconds(), d.getMilliseconds())
  return utc_ts;
}

$.widget( "custom.etimeseries", {
    options: {
        theme: "default",
        data_url: null,
        show_series_select: true,
        show_timeline: true,
        range: null,
        chart_div:null,
        chart: null,
        timeline: null,
        dialog: null,
        id: "unknown"
    },

    _adjust_options: function(options) {
      options["toolbox"]["feature"]["mySeriesTool"] = {
        show: true,
        title: 'Series Settings',
        icon: 'path://M8.2,38.4l-8.4,4.1l30.6,15.3L60,42.5l-8.1-4.1l-21.5,11L8.2,38.4z M51.9,30l-8.1,4.2l-13.4,6.9l-13.9-6.9L8.2,30l-8.4,4.2l8.4,4.2l22.2,11l21.5-11l8.1-4.2L51.9,30z M51.9,21.7l-8.1,4.2L35.7,30l-5.3,2.8L24.9,30l-8.4-4.1l-8.3-4.2l-8.4,4.2L8.2,30l8.3,4.2l13.9,6.9l13.4-6.9l8.1-4.2l8.1-4.1L51.9,21.7zM30.4,2.2L-0.2,17.5l8.4,4.1l8.3,4.2l8.4,4.2l5.5,2.7l5.3-2.7l8.1-4.2l8.1-4.2l8.1-4.1L30.4,2.2',
        onclick: this.open_settings.bind(this)};
      return options;
    },

    open_settings: function() {
      this.options.dialog.empty();
      var content = jQuery('<div/>');
      $.each(this.options.series_info, function( key, value ) {
        var p = content.append(jQuery('<p/>'))
        var cb = p.append(jQuery('<input/>', {type: "checkbox", id: "cb_" + key}))
        p.append(key);
        content.append(p);
        //content.append($("<p><input type='checkbox' id='cb_" + key + "' ><label for='cb_" + key + "'>" + key + "</label></p>"))
      });
      content.appendTo(this.options.dialog);
      this.options.dialog.dialog("open");
    },

    _save_dialog: function() {
      d = this.options.dialog;
      d.children("input:checkbox").each(function( index ) {
        console.log( index + ": " + $( this ).text() );
      });
    },

    _create_dialog: function() {
      var dialog_id = uniqId();
      var dialog = jQuery('<div/>', {
        "id": dialog_id,
        "class": 'etimeseries-dialog',
        "style": "display: none;",
        "title": "Mein toller Dialog"});
      var self = this;
      dialog.dialog({
        autoOpen: false,
        buttons: {
          "save": function() {self._save_dialog()}
        }
      });
      return dialog;
    },

    _create: function() {
        var theme = this.options.theme;
        var show_series_select = this.options.show_series_select;
        var show_timeline = this.options.show_timeline;
        var series_info = this.options.series_info;
        var l = this.options.limits;

        // Adjust Opt
        this.options.options = this._adjust_options(this.options.options)
        var o = this.options.options;

        var height = this.element.height();
        var chart_div = jQuery('<div/>', {
            "id": uniqId(),
            "class": 'etimeseries-chart',
            "style": "width: 100%;"});
        chart_div.height(height);
        var timeline_div = jQuery('<div/>', {
            "id": uniqId(),
            "class": 'etimeseries-timeline',
            "style": "width: 90%; margin: auto;"});

        var default_min = Date.parse(l.dt_max_iso) - (24*60*60*1000) * l.default_days;
        var default_max = Date.parse(l.dt_max_iso);
        this.options.range = [default_min, default_max];

        timeline_div.dateRangeSlider({
            bounds:{
                min: Date.parse(l.dt_min_iso),
                max: Date.parse(l.dt_max_iso)
            },
            defaultValues:{
                min: this.options.range[0],
                max: this.options.range[1]
            },
            range:{
                min: {days: l.min_days},
                max: {days: l.max_days}
            }
        });

        chart_div.appendTo(this.element);
        if (show_timeline) {
            timeline_div.appendTo(this.element);
        }
        var dialog_div = this._create_dialog();
        this.options.dialog = dialog_div;

        var chart = echarts.init(chart_div[ 0 ]);
        chart.setOption(o);

        // On Chart Zoom
        chart.on('dataZoom', this._handle_zoom.bind(this));

        // On Chart Reset
        chart.on('restore', this._handle_restore.bind(this));

        // On Timeline Changed
        timeline_div.on("userValuesChanged", this._handle_slider_move.bind(this));

        this.options.chart = chart;
        this.options.chart_div = chart_div;
        this.options.timeline = timeline_div;

        $(window).on('resize', function(){
            chart.resize();
        });
        setTimeout(function(){ chart.resize(); }, 50);
    },

    _handle_zoom: function (params) {
      var chart = this.options.chart;
      var axis = chart.getModel().option.xAxis[0];
      var d1, d2 = null;
      if (axis.rangeStart){
        d1 = new Date(axis.rangeStart);
      } else {
        d1 = this.options.range[0];
      }
      if (axis.rangeEnd){
        d2 = new Date(axis.rangeEnd);
      } else {
        d2 = this.options.range[1];
      }
      this.options.timeline.dateRangeSlider("values", d1, d2);
      console.log("zoom", params);
    },

    _handle_restore: function (params) {
      var chart = this.options.chart;
      var axis = chart.getModel().option.xAxis[0];
      var d1 = this.options.range[0];
      var d2 = this.options.range[1];
      this.options.timeline.dateRangeSlider("values", d1, d2);
      console.log("restore");
    },

    _handle_slider_move: function(e, data) {
      current_range = [data.values.min, data.values.max];
      console.log("slider moved", data.values.min, data.values.max);
      var start_day = data.values.min;
      start_day.setHours(0,0,0,0);
      var end_day = data.values.max;
      end_day.setHours(23,59,59,999);
      var min = timeAsUTCDate(start_day);
      var max = timeAsUTCDate(end_day);
      this.set_zoom(min, max, false);
      // this.set_zoom(data.values.min, data.values.max, false);
    },

    load_data: function(f, t) {
      var chart = this.options.chart;
      chart.showLoading();
      var f_value = new Date(f);
      //f_value.setHours(0,0,0,0);
      var t_value = new Date(t);
      //t_value.setHours(23,59,59,999);
      var f_iso = f_value.toISOString().substring(0, 10);
      var t_iso = t_value.toISOString().substring(0, 10);
      var req_url = this.options.data_url;
      var req_data = {from_date: f_iso, to_date: t_iso, action: "data", chart_id: this.options.id};
      console.log("get_data", req_url);

      var self = this;
      $.ajax({
        type: "POST",
        url: req_url,
        data: JSON.stringify(req_data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
          var opt = {dataset: data};
          chart.setOption(opt);
          self.options.range[0] = f;
          self.options.range[1] = t;
          chart.dispatchAction({
            type: 'dataZoom',
            startValue: f_value.getTime(),
            endValue: t_value.getTime()
          });
          chart.hideLoading();
        },
        failure: function(errMsg) {
            alert(errMsg);
        }
      });
      // $.getJSON(req_url, function( data ) {
      //   var opt = {dataset: data};
      //   chart.setOption(opt);
      //   self.options.range[0] = f;
      //   self.options.range[1] = t;
      //   chart.dispatchAction({
      //     type: 'dataZoom',
      //     startValue: f_value.getTime(),
      //     endValue: t_value.getTime()
      //   });
      //   chart.hideLoading();
      // });
    },

    set_zoom: function(f, t, adjust_slider=true) {
        var current_min = this.options.range[0];
        var current_max = this.options.range[1];
        var chart = this.options.chart;

        if (f < current_min || t > current_max) {
          // we need new data
          this.load_data(f, t);
          return;
        }

        // Move Chart
        chart.dispatchAction({
          type: 'dataZoom',
          startValue: f,
          endValue: t
        });

        if (adjust_slider) {
          this.options.timeline.dateRangeSlider("values", f, t);
        }
    },
});