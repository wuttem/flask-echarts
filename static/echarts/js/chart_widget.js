$.widget( "custom.etimeseries", {
    options: {
        theme: "default",
        show_series_select: true,
        show_timeline: true
    },

    _create: function() {
        var theme = this.options.theme;
        var show_series_select = this.options.show_series_select;
        var show_timeline = this.options.show_timeline;
        this.element
            .addClass( "progressbar" )
            .text( progress );
    }
});