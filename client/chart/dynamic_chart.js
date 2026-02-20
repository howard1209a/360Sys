const totalThroughputData = [];
const totalBandwidthData = [];
const bitrateSelectData = [];
const bufferLengthData = [];
const viewDataX = [];
const viewDataY = [];
const lowQualityData = [];
const viewBitrateData = [];

const maxDataPoints = 30;

const bitrateSelectColor = [
  "greem",
  "red",
  "blue",
  "black",
  "yellow",
  "rgba(0, 0, 255, 0.5)",
];

var totalThroughputChart = null;
var totalBandwidthChart = null;
var bitrateSelectChart = null;
var bufferLengthChart = null;
var viewChart = null;
var lowQualityChart = null;
var viewBitrateChart = null;

function initChart() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  // 网络吞吐速率图
  totalThroughputChart = new Chart(
    document.getElementById("totalThroughputChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "",
            borderColor: "blue",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false, // 隐藏图例
          },
          tooltip: {
            enabled: true, // 保持工具提示
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: "时间戳(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10,
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "网络吞吐速率(MB/s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              callback: function (value) {
                return value.toFixed(2);
              },
            },
          },
        },
      },
    }
  );

  // 网络带宽速率图
  totalBandwidthChart = new Chart(
    document.getElementById("totalBandwidthChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "",
            borderColor: "blue",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false, // 隐藏图例
          },
          tooltip: {
            enabled: true, // 保持工具提示
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: "时间戳(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10,
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "网络带宽速率(MB/s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              callback: function (value) {
                return value.toFixed(2);
              },
            },
          },
        },
      },
    }
  );

  // 瓦片码率选择图
  var bitrateSelectDatasets = [];
  for (let i = 0; i < $scope.playerCount; i++) {
    bitrateSelectDatasets[i] = {
      label: "Tile" + i,
      borderColor: bitrateSelectColor[i],
      fill: false,
      data: [],
    };
    bitrateSelectData[i] = [];
  }
  bitrateSelectChart = new Chart(
    document.getElementById("bitrateSelectChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: bitrateSelectDatasets,
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true, // 隐藏图例
            labels: {
              font: {
                size: 20,
              },
            },
          },
          tooltip: {
            enabled: true, // 保持工具提示
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: "时间戳(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10,
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "瓦片码率选择(kbps)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              callback: function (value) {
                return value.toFixed(0);
              },
            },
          },
        },
      },
    }
  );

  // 缓冲区长度图
  bufferLengthChart = new Chart(
    document.getElementById("bufferLengthChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "",
            borderColor: "blue",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false, // 隐藏图例
          },
          tooltip: {
            enabled: true, // 保持工具提示
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: "时间戳(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10,
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "缓冲区长度(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              callback: function (value) {
                return value.toFixed(2);
              },
            },
          },
        },
      },
    }
  );

  // 视野角度图
  viewChart = new Chart(document.getElementById("viewChart").getContext("2d"), {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "水平视野角度X",
          borderColor: "red",
          fill: false,
          data: [],
          yAxisID: "y",
        },
        {
          label: "垂直视野角度Y",
          borderColor: "green",
          fill: false,
          data: [],
          yAxisID: "y1",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          labels: {
            font: {
              size: 20,
            },
          },
        },
        tooltip: {
          enabled: true,
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "时间戳(s)",
            font: {
              size: 20,
            },
            color: "#333",
          },
          ticks: {
            font: {
              size: 20,
            },
            color: "#666",
            maxRotation: 0,
            minRotation: 0,
            autoSkip: true,
            maxTicksLimit: 10,
          },
        },
        y: {
          beginAtZero: true,
          position: "left",
          title: {
            display: true,
            text: "水平视野角度X(°)",
            font: {
              size: 20,
            },
            color: "#333",
          },
          ticks: {
            font: {
              size: 20,
            },
            color: "#666",
            callback: function (value) {
              return value.toFixed(2);
            },
          },
        },
        y1: {
          beginAtZero: true,
          position: "right",
          title: {
            display: true,
            text: "垂直视野角度Y(°)",
            font: {
              size: 20,
            },
            color: "#333",
          },
          ticks: {
            font: {
              size: 20,
            },
            color: "#666",
            callback: function (value) {
              return value.toFixed(2);
            },
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    },
  });

  // 视野内低质量区域比例图
  lowQualityChart = new Chart(
    document.getElementById("lowQualityChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "",
            borderColor: "blue",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false, // 隐藏图例
          },
          tooltip: {
            enabled: true, // 保持工具提示
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: "时间戳(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10,
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "视野内低质量区域比例(%)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              callback: function (value) {
                return value.toFixed(0);
              },
            },
          },
        },
      },
    }
  );

  // 视野内画面比特率图
  viewBitrateChart = new Chart(
    document.getElementById("viewBitrateChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "",
            borderColor: "blue",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false, // 隐藏图例
          },
          tooltip: {
            enabled: true, // 保持工具提示
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: "时间戳(s)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10,
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "视野内画面比特率(kbps)",
              font: {
                size: 20,
              },
              color: "#333",
            },
            ticks: {
              font: {
                size: 20,
              },
              color: "#666",
              callback: function (value) {
                return value.toFixed(0);
              },
            },
          },
        },
      },
    }
  );

  // 启动定时器定期更新图表数据
  setInterval(updateClientStats, 1000);
}

function updateClientStats() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  totalThroughputData.push(($scope.totalThroughput / 8000000).toFixed(2));
  if (totalThroughputData.length > maxDataPoints) {
    totalThroughputData.shift();
  }

  totalBandwidthData.push(($scope.totalBandwidth / 8000000).toFixed(2));
  if (totalBandwidthData.length > maxDataPoints) {
    totalBandwidthData.shift();
  }

  for (let i = 0; i < $scope.playerCount; i++) {
    var tile_quality = $scope.players[i].getQualityFor("video");
    bitrate =
      $scope.players[i].getBitrateInfoListFor("video")[tile_quality].bitrate;
    bitrateSelectData[i].push(bitrate / 1000);
    if (bitrateSelectData[i].length > maxDataPoints) {
      bitrateSelectData[i].shift();
    }
  }

  bufferLengthData.push($scope.playerBufferLength[0].toFixed(2));
  if (bufferLengthData.length > maxDataPoints) {
    bufferLengthData.shift();
  }

  // 在bufferLengthData.push后面添加
  viewDataX.push(
    (($scope.current_center_viewport_x * 180) / 3.1415926 + 180).toFixed(0)
  );
  viewDataY.push(
    (($scope.current_center_viewport_y * 180) / 3.1415926 + 180).toFixed(0)
  );
  if (viewDataX.length > maxDataPoints) {
    viewDataX.shift();
    viewDataY.shift();
  }

  lowQualityData.push(($scope.low_quality_ratio * 100).toFixed(0));
  if (lowQualityData.length > maxDataPoints) {
    lowQualityData.shift();
  }

  viewBitrateData.push(($scope.bitrate_in_view / 1000).toFixed(0));
  if (viewBitrateData.length > maxDataPoints) {
    viewBitrateData.shift();
  }

  updateCharts();
}

function updateCharts() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  const totalThroughputLabels = Array.from(
    { length: totalThroughputData.length },
    (_, index) => index + 1
  );
  totalThroughputChart.data.labels = totalThroughputLabels;
  totalThroughputChart.data.datasets[0].data = totalThroughputData.slice();
  totalThroughputChart.update();

  const totalBandwidthLabels = Array.from(
    { length: totalBandwidthData.length },
    (_, index) => index + 1
  );
  totalBandwidthChart.data.labels = totalBandwidthLabels;
  totalBandwidthChart.data.datasets[0].data = totalBandwidthData.slice();
  totalBandwidthChart.update();

  const bitrateSelectLabels = Array.from(
    { length: bitrateSelectData[0].length },
    (_, index) => index + 1
  );
  bitrateSelectChart.data.labels = bitrateSelectLabels;
  for (let i = 0; i < $scope.playerCount; i++) {
    bitrateSelectChart.data.datasets[i].data = bitrateSelectData[i].slice();
  }
  bitrateSelectChart.update();

  const bufferLengthLabels = Array.from(
    { length: bufferLengthData.length },
    (_, index) => index + 1
  );
  bufferLengthChart.data.labels = bufferLengthLabels;
  bufferLengthChart.data.datasets[0].data = bufferLengthData.slice();
  bufferLengthChart.update();

  const viewLabels = Array.from(
    { length: viewDataX.length },
    (_, index) => index + 1
  );
  viewChart.data.labels = viewLabels;
  viewChart.data.datasets[0].data = viewDataX.slice();
  viewChart.data.datasets[1].data = viewDataY.slice();
  viewChart.update();

  const lowQualityLabels = Array.from(
    { length: lowQualityData.length },
    (_, index) => index + 1
  );
  lowQualityChart.data.labels = lowQualityLabels;
  lowQualityChart.data.datasets[0].data = lowQualityData.slice();
  lowQualityChart.update();

  const viewBitrateLabels = Array.from(
    { length: viewBitrateData.length },
    (_, index) => index + 1
  );
  viewBitrateChart.data.labels = viewBitrateLabels;
  viewBitrateChart.data.datasets[0].data = viewBitrateData.slice();
  viewBitrateChart.update();
}
