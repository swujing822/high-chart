// 时间戳按10秒分组，返回格式 HH:MM:SS （秒是10的倍数）
function groupTimeByTenSeconds(timestamp) {
  const d = new Date(timestamp);
  const HH = d.getHours().toString().padStart(2, "0");
  const MM = d.getMinutes().toString().padStart(2, "0");
  const SS = d.getSeconds();
  const tenSec = Math.floor(SS / 10) * 10;
  const tenSecStr = tenSec.toString().padStart(2, "0");
  return `${HH}:${MM}:${tenSecStr}`;
}

function initTabulatorTable(selector, data) {
  // 生成 Exchange 过滤选项
  const uniqueExchanges = [...new Set(data.map(item => item.exchange))];
  const exchangeFilterValues = { "": "All" };
  uniqueExchanges.forEach(ex => {
    exchangeFilterValues[ex] = ex;
  });

  // 生成10秒级时间过滤选项
  const uniqueTenSeconds = new Set();
  data.forEach(item => {
    if (!item.timestamp) return;
    const key = groupTimeByTenSeconds(item.timestamp);
    uniqueTenSeconds.add(key);
  });

  const tenSecondFilterValues = { "": "All" };
  [...uniqueTenSeconds].sort().forEach(t => {
    tenSecondFilterValues[t] = t;
  });

  // 初始化 Tabulator
  return new Tabulator(selector, {
    height: "500px",
    layout: "fitColumns",
    data: data,
    columns: [
      { title: "Timestamp", field: "timestamp", visible: true }, // 隐藏时间戳列
      { title: "Time", field: "time", headerFilter: "input"},
      {
        title: "Time (10s)",
        field: "time",
        headerFilter: "select",
        headerFilterParams: {
          values: tenSecondFilterValues,
          clearable: true,
        },
        headerFilterFunc: function (headerValue, rowValue, rowData) {
          if (!headerValue) return true;
          if (!rowData.timestamp) return false;
          return groupTimeByTenSeconds(rowData.timestamp) === headerValue;
        },
      },
      {
        title: "Exchange",
        field: "exchange",
        headerFilter: "select",
        headerFilterParams: {
          values: exchangeFilterValues,
          clearable: true,
        },
      },
      { title: "Symbol", field: "symbol", headerFilter: "input" },
      {
        title: "Bid1 Price",
        field: "bid1_price",
        sorter: "number",
        // formatter: "money",
      },
      {
        title: "Ask1 Price",
        field: "ask1_price",
        sorter: "number",
        // formatter: "money",
      },
    ],
  });
}
