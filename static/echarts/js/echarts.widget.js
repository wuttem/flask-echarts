function uniqId() {
    return Math.round(new Date().getTime() + (Math.random() * 100));
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
        timeline: null
    },

    _create: function() {
        var theme = this.options.theme;
        var show_series_select = this.options.show_series_select;
        var show_timeline = this.options.show_timeline;
        var l = this.options.limits;
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
            "style": "width: 80%; margin: auto;"});

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
        
        var chart = echarts.init(chart_div[ 0 ]);
        chart.setOption(o);

        // On Chart Zoom
        chart.on('dataZoom', function (params) {
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
            timeline_div.dateRangeSlider("values", d1, d2);
            console.log("zoom", params);
        });

        // On Chart Reset
        chart.on('restore', function (params) {
            var axis = chart.getModel().option.xAxis[0];
            var d1 = this.options.range[0];
            var d2 = this.options.range[1];
            timeline_div.dateRangeSlider("values", d1, d2);
            console.log("restore");
        });

        // On Timeline Changed
        timeline_div.on("userValuesChanged", function(e, data){
            current_range = [data.values.min, data.values.max];
            console.log("slider moved", data.values.min, data.values.max);
            this.set_zoom(data.values.min, data.values.max);
        });

        chart_div.appendTo(this.element);
        if (show_timeline) {
            timeline_div.appendTo(this.element);
        }

        this.options.chart = chart;
        this.options.chart_div = chart_div;
        this.options.timeline = timeline_div;

        $(window).on('resize', function(){
            chart.resize();
        });
        setTimeout(function(){ chart.resize(); }, 50);


        // this.element
        //     .addClass( "etimeseries" )
        //     .text( progress );
    },

    set_zoom: function(f, t) {
        var current_min = this.options.range[0];
        var current_max = this.options.range[1];
        var chart = this.options.chart;
      
        if (f < current_min || t > current_max) {
          // we need new data
          chart.showLoading();
          var f_value = new Date(f);
          f_value.setHours(0,0,0,0);
          var t_value = new Date(t);
          t_value.setHours(23,59,59,999);
          var f_iso = f_value.toISOString().substring(0, 10);
          var t_iso = t_value.toISOString().substring(0, 10);
          var req_url = this.options.data_url + "&from_date=" + f_iso + "&to_date=" + t_iso;
          console.log("get_data", req_url);
          $.getJSON(req_url, function( data ) {
            var opt = {dataset: data};
            chart.setOption(opt);
            this.options.range[0] = f;
            this.options.range[1] = t;
            chart.dispatchAction({
              type: 'dataZoom',
              startValue: f_value.getTime(),
              endValue: t_value.getTime()
            });
            chart.hideLoading();
          });
          return;
        }
      
        // Move Chart
        chart.dispatchAction({
          type: 'dataZoom',
          startValue: f,
          endValue: t
        });
    },
});