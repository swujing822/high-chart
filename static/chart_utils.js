
function calculateArbitrageSpread(data) {
    // 按秒级时间戳分组数据
    const timeMap = {};
    data.forEach((e, index) => {
        // 检查时间戳是否有效
        const d = new Date(e.timestamp);
        const HH = d.getHours().toString().padStart(2, "0");
        const MM = d.getMinutes().toString().padStart(2, "0");
        const SS = d.getSeconds();
        // parsedDate.setHours(parsedDate.getHours() + 8);
        const secondLevelTime = `${HH}:${MM}:${SS}`;
        if (!timeMap[secondLevelTime]) timeMap[secondLevelTime] = [];
        timeMap[secondLevelTime].push(e);
    });


    // 计算套利差价 (taker-taker: 最高买价 - 最低卖价)
    const arbitrageData = Object.keys(timeMap).map(time => {
        const records = timeMap[time];

        const bids = records.map(d => ({ exchange: d.exchange, price: d.bid1_price, timestamp: d.timestamp, time: d.time }));
        const asks = records.map(d => ({ exchange: d.exchange, price: d.ask1_price, timestamp: d.timestamp, time: d.time }));

        const highestBid = bids.reduce((max, b) => b.price > max.price ? b : max, { price: -Infinity });
        const lowestAsk = asks.reduce((min, a) => a.price < min.price ? a : min, { price: Infinity });

        const spread = highestBid.price - lowestAsk.price;
        const spreadPercent = lowestAsk.price !== 0 ? (spread / lowestAsk.price) * 100 : 0;

        var list = [Math.min(lowestAsk.timestamp, highestBid.timestamp), spreadPercent, lowestAsk, highestBid, records];
        return list;
    });

    const maxPoint = arbitrageData.reduce((prev, curr) => {
        return curr[1] > prev[1] ? curr : prev;
    });


    return {
        name: "Arbitrage Spread (%)",
        data: arbitrageData,
        type: 'scatter',  // ✅ 明确声明类型
        color: "#4363d8",
        dataLabels: {
            enabled: true,
            formatter: function () {
                if (this.x === maxPoint[0] && this.y === maxPoint[1]) {
                    return `${this.y.toFixed(5)}%`;  // 标出最大套利百分比
                }
                return null;
            },
            style: {
                color: 'red',
                // fontWeight: 'bold'
            },
            y: -5,
            x: -15,
        }
    };
}


function drawData(data, fileName) {

    const customColors = [
        '#FF6B6B', // 鲜红
        // '#4ECDC4', // 薄荷绿
        '#1A535C', // 墨绿蓝
        '#2E86AB', // 天蓝
        '#D7263D', // 暗红
        '#A1C181', // 浅橄榄绿
        '#E76F51', // 赤陶橙
        '#3cb44b', // 明亮绿
        '#4363d8', // 亮蓝
        '#f58231', // 橙色
        '#911eb4', // 紫色
        '#f032e6', // 粉紫
        '#d3f583'
    ];

    const exchangeColorMap = {};
    let colorIndex = 0;
    const exchanges = [...new Set(data.map(d => d.exchange))].sort();


    exchanges.forEach(exchange => {
        exchangeColorMap[exchange] = customColors[colorIndex % customColors.length];
        colorIndex++;
    });


    const bidSeries = [];
    const askSeries = [];

    exchanges.forEach(ex => {
        const filtered = data.filter(d => d.exchange === ex);

        bidSeries.push({
            name: `${ex} bid1`,
            data: filtered.map(d => [d.timestamp, d.bid1_price]),
            dashStyle: 'Dash',
            lineWidth: 2,
            color: exchangeColorMap[ex],
            marker: { enabled: false }
        });

        askSeries.push({
            name: `${ex} ask1`,
            data: filtered.map(d => [d.timestamp, d.ask1_price]),
            dashStyle: 'Solid',
            lineWidth: 1,
            color: exchangeColorMap[ex],
            marker: { enabled: false }
        });
    });


    allSeries = [...bidSeries, ...askSeries]

    allSeries = allSeries.sort((a, b) => {
        return a.name.localeCompare(b.name);
    });

    /////////////////////////////////


    ///////////////////////////////////


    Highcharts.chart('container', {
        chart: {
            type: 'line',
            animation: false,  // 关闭动画
            events: {
                load() {
                    const chart = this;
                    let allVisible = true;

                    chart.renderer.button('隐藏/显示', 10, 10, function () {
                        chart.series.forEach(s => {
                            s.setVisible(!allVisible, false);
                        });
                        chart.redraw();
                        allVisible = !allVisible;
                    }, {
                        width: 60,             // 宽度缩小
                        height: 16,             // 高度缩小
                        padding: 5,             // 内边距
                        r: 3,                   // 圆角稍微调整
                        fill: '#e6e6e6',
                        stroke: '#999',
                        'stroke-width': 1
                    }, {
                        fill: '#ccc',
                        style: {
                            color: 'black'
                        }
                    }).add();
                }
            }
        },
        title: {
            text: `Bid1 vs Ask1 by Exchange - ${fileName}`
        },
        // title: { text: 'Bid1 vs Ask1 by Exchange' },
        xAxis: {
            type: 'datetime',      // ⭐️ 关键：使用时间戳作为横轴
            title: { text: '' },
            labels: { rotation: -35 }
        },
        yAxis: { title: { text: '价格（USDT）' } },
        tooltip: { shared: true, crosshairs: true },
        legend: {
            padding: 1,           // legend 容器内边距，默认12左右，调小让整体更紧凑
            itemMarginTop: 1,
            itemMarginBottom: 1,
            symbolPadding: 1,     // 标记和文字间距，默认一般是5，调小让更紧凑
            itemStyle: {
                padding: 0          // legend 条目文字本身的内边距，通常设0即可
            }
        },
        series: allSeries,
        plotOptions: {
            series: {
                animation: false
            }
        },
    });

    ///////////////////////

    const diffSeries = [];

    exchanges.forEach(ex => {
        const filtered = data.filter(d => d.exchange === ex);

        diffSeries.push({
            name: `${ex} bid1`,
            data: filtered.map(d => [d.timestamp, 100 * (d.ask1_price - d.bid1_price) / d.bid1_price]),
            // dashStyle: 'Dash',
            lineWidth: 1,
            color: exchangeColorMap[ex],
            marker: { enabled: false }
        });
    });


    var arbitrageSeries = calculateArbitrageSpread(data);
    diffSeries.push(arbitrageSeries)

    console.log("diff>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    console.log(diffSeries)

    Highcharts.chart('container2', {
        chart: {
            type: 'scatter',
            animation: false,  // 关闭动画

            marginTop: 10 // 确保标题和按钮空间
        },
        title: {
            // text: `Arbitrage Spread (%) - ${fileName}`
            text: ''
        },
        xAxis: {
            type: 'datetime',      // ⭐️ 关键：使用时间戳作为横轴
            title: { text: '' },
            labels: { rotation: -35 },
            labels: {
                enabled: false
            }
        },
        yAxis: {
            title: {
                text: '套利差价（%）',
            },
            labels: {
                format: '{value}%',
            },
            lineWidth: 0.5
        },
        legend: { enabled: true },
        // series: [arbitrageSeries],
        series: diffSeries,
        // tooltip: {
        //     formatter: function () {
        //         const pointIndex = this.point.index;
        //         const dataPoint = arbitrageSeries.data[pointIndex];

        //         var records = dataPoint[4];
        //         // var html = ""
        //         // records.forEach(e => {
        //         //     html += e.exchange + " ask1:" + e.ask1_price + ", bid1:" + e.bid1_price + "<br />"
        //         //     // html += e.exchange + " bid1:" + e.bid1_price + "<br />"
        //         // });

        //         const timestamp = dataPoint[0];
        //         const date = new Date(timestamp - 8 * 60 * 60 * 1000);  // 时间戳加8小时（毫秒）
        //         const formattedTime = date.toTimeString().split(' ')[0]; // "HH:MM:SS"

        //         return `<b>时间：</b> ${formattedTime}<br/>
        // <b>套利差价：</b> ${dataPoint[1]}%<br/>
        // <b>Best Buy Exchange：</b> ${dataPoint[2].exchange} buy: ${dataPoint[2].price}<br/>
        // <b>Best Sell Exchange：</b> ${dataPoint[3].exchange} sell: ${dataPoint[3].price}<br/>`;
        //     }
        // },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 2  // 点的半径，单位：像素，默认是 4
                }
            },
            series: {
                animation: false
            }
        }

    });

    return diffSeries;
}