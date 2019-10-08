(function (root, factory) {if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module.
    define(['exports', 'echarts'], factory);
} else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    // CommonJS
    factory(exports, require('echarts'));
} else {
    // Browser globals
    factory({}, root.echarts);
}
}(this, function (exports, echarts) {
var log = function (msg) {
    if (typeof console !== 'undefined') {
        console && console.error && console.error(msg);
    }
};
if (!echarts) {
    log('ECharts is not Loaded');
    return;
}

var colorPalette = [
    '#AFB505','#999999','#4484B8','#555555',
    '#DE9610','#D13D3D','#333333','#6741D1'
];

var theme = {

    color: colorPalette,

    title: {
        textStyle: {
            fontWeight: 'normal',
            color: '#021512'
        }
    },

    visualMap: {
        color:['#021512','#a2d4e6']
    },

    toolbox: {
        color : ['#021512','#021512','#021512','#021512']
    },

tooltip: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    axisPointer : {            // Axis indicator, coordinate trigger effective
        type : 'line',         // The default is a straight line： 'line' | 'shadow'
        lineStyle : {          // Straight line indicator style settings
            color: '#021512',
            type: 'dashed'
        },
        crossStyle: {
            color: '#021512'
        },
        shadowStyle : {                     // Shadow indicator style settings
            color: 'rgba(200,200,200,0.3)'
        }
    }
},

// Area scaling controller
dataZoom: {
    dataBackgroundColor: '#eee',            // Data background color
    fillerColor: 'rgba(144,197,237,0.2)',   // Fill the color
    handleColor: '#021512'     // Handle color
},

timeline : {
    lineStyle : {
        color : '#021512'
    },
    controlStyle : {
        normal : { color : '#021512'},
        emphasis : { color : '#021512'}
    }
},

k: {
    itemStyle: {
        normal: {
            color: '#043a47',          // Yang line filled with color
            color0: '#087891',      // Yinxian fill color
            lineStyle: {
                width: 1,
                color: '#b31d14',   // Yang line border color
                color0: '#c8c8c8'   // Yinbian border color
            }
        }
    }
},

    candlestick: {
        itemStyle: {
            normal: {
                color: '#021512',
                color0: '#a2d4e6',
                lineStyle: {
                    width: 1,
                    color: '#021512',
                    color0: '#a2d4e6'
                }
            }
        }
    },

    graph: {
        color: colorPalette
    },

    map: {
    itemStyle: {
        normal: {
            areaStyle: {
                color: '#ddd'
            },
            label: {
                textStyle: {
                    color: '#c12e34'
                }
            }
        },
        emphasis: {                 // Is also selected style
            areaStyle: {
                color: '#087891'
            },
            label: {
                textStyle: {
                    color: '#c12e34'
                }
            }
        }
    }
},

force : {
    itemStyle: {
        normal: {
            linkStyle : {
                color : '#021512'
            }
        }
    }
},

    gauge : {
    axisLine: {            // Coordinate axis
        show: true,        // Default display, property show control display or not
        lineStyle: {       // Attribute lineStyle controls the line style
            color: [[0.2, '#043a47'],[0.8, '#021512'],[1, '#b31d14']],
            width: 8
        }
    },
    axisTick: {            // Small mark of the axis
        splitNumber: 10,   // How many segments per split subdivision
        length :12,        // Attribute length control line length
        lineStyle: {       // Attribute lineStyle controls the line style
            color: 'auto'
        }
    },
    axisLabel: {           // Axis text label, see details axis.axisLabel
        textStyle: {       // The remaining attributes use the global text style by default TEXTSTYLE
            color: 'auto'
        }
    },
    splitLine: {           // Separate lines
        length : 18,         // Attribute length control line length
        lineStyle: {       // The attribute lineStyle (see lineStyle for details) controls the line style
            color: 'auto'
        }
    },
    pointer : {
        length : '90%',
        color : 'auto'
    },
    title : {
        textStyle: {       // The remaining attributes use the global text style by default TEXTSTYLE
            color: '#333'
        }
    },
    detail : {
        textStyle: {       // The remaining attributes use the global text style by default TEXTSTYLE
            color: 'auto'
        }
    }
}
};
echarts.registerTheme('some', theme);
}));