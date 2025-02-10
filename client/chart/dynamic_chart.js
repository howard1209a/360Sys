// 使用 Chart.js 库绘制动态折线图
const bitrateSelectColor = [
  "greem",
  "red",
  "blue",
  "black",
  "yellow",
  "rgba(0, 0, 255, 0.5)",
];

const throughputData = [];
const bitrateSelectData = [];
const energyUsageData = [];

const maxDataPoints = 30; // 设置最大数据点数量

// 初始化图表
var throughputChart = null;
var bitrateSelectChart = null;
var energyChart = null;

function initChart() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  // 初始化吞吐量图表
  throughputChart = new Chart(
    document.getElementById("throughputChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [], // 空数组初始化
        datasets: [
          {
            label: "Throughput (MB/s)",
            borderColor: "blue",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { beginAtZero: true },
          y: { beginAtZero: true },
        },
      },
    }
  );

  var bitrateSelectDatasets = [];
  // 初始化比特率选择图表
  for (let i = 0; i < $scope.playerCount; i++) {
    bitrateSelectDatasets[i] = {
      label: "tile" + i,
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
        scales: {
          x: { beginAtZero: true },
          y: { beginAtZero: true },
        },
      },
    }
  );

  // 初始化能耗图表
  energyChart = new Chart(
    document.getElementById("energyChart").getContext("2d"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Energy Consumption (W)",
            borderColor: "red",
            fill: false,
            data: [],
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { beginAtZero: true },
          y: { beginAtZero: true },
        },
      },
    }
  );

  // 启动定时器定期更新图表数据
  setInterval(updateClientStats, 1000);
}

// 获取客户端信息并更新
function updateClientStats() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  // 模拟数据更新（实际应用中可以根据需要获取真实数据）
  const currentEnergyUsage = Math.random() * 10 + 20; // 模拟能耗

  // 更新折线图数据
  throughputData.push(($scope.totalThroughput / 8000000).toFixed(2));
  // 保持数据点数量不超过最大数量
  if (throughputData.length > maxDataPoints) {
    throughputData.shift();
  }

  for (let i = 0; i < $scope.playerCount; i++) {
    bitrateSelectData[i].push($scope.players[i].getQualityFor("video"));
    if (bitrateSelectData[i].length > maxDataPoints) {
      bitrateSelectData[i].shift();
    }
  }

  // 更新折线图
  updateCharts();
}

// 绘制折线图
function updateCharts() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  // 为每个数据点生成对应的标签
  const labels = Array.from(
    { length: throughputData.length },
    (_, index) => index + 1
  );

  // 吞吐量图表
  throughputChart.data.labels = labels;
  throughputChart.data.datasets[0].data = throughputData.slice();
  throughputChart.update();

  bitrateSelectChart.data.labels = labels;
  for (let i = 0; i < $scope.playerCount; i++) {
    bitrateSelectChart.data.datasets[i].data = bitrateSelectData[i].slice();
  }
  bitrateSelectChart.update();

  //   // 能耗图表
  //   energyChart.data.labels = labels;
  //   energyChart.data.datasets[0].data = energyUsageData;
  //   energyChart.update();
}
