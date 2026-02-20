var SPB360Rule;

function SPB360RuleClass() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();
  let factory = dashjs.FactoryMaker;
  let SwitchRequest = factory.getClassFactoryByName("SwitchRequest");
  let context = this.context;
  let instance;

  // 常量定义（与仿真一致）
  const M = 90; // 水平视野（度）
  const N = 90; // 垂直视野（度）
  const ETA = 2; // 黑边惩罚系数
  const L_MIN = 0.5; // 最小片段时长（秒）
  const L_MAX = 6; // 最大片段时长（秒）
  const K_MIN = 0; // 最小扩展角（度）
  const K_MAX = Math.max((180 - N) / 2, (360 - M) / 2); // 约135度
  const BIT2MB = 8388608.0; // bit转MB因子
  const S_T_REDUNDANCY = 1.0; // 数据冗余系数

  // 网格搜索参数（离散化）
  const L_STEPS = 5; // l维度的采样点数
  const K_STEPS = 10; // k维度的采样点数

  // 标准正态分布CDF近似（Abramowitz and Stegun）
  function normCDF(x) {
    var t = 1 / (1 + 0.2316419 * Math.abs(x));
    var d = 0.3989423 * Math.exp((-x * x) / 2);
    var p =
      d *
      t *
      (0.3193815 +
        t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return x > 0 ? 1 - p : p;
  }

  // 初始化或获取共享状态
  function getSharedState() {
    if (!$scope.spb360) {
      $scope.spb360 = {
        // 带宽模型
        bandwidthHistory: [], // 历史吞吐量（MB）
        bandwidthMean: 1.0, // 均值
        bandwidthVariance: 0.1, // 方差

        // 运动模型（加速度）
        motionHistory: [], // 历史视角 {timestamp, yaw, pitch}
        aXMean: 0,
        aXStd: 1, // 水平加速度均值/标准差
        aYMean: 0,
        aYStd: 1, // 垂直加速度均值/标准差

        // 上次优化结果
        lastOptimizeTime: 0,
        bestL: L_MIN,
        bestK: K_MIN,
        eovFaces: {}, // 当前EOV内的面（可见面集合）

        // 辅助：上次视角用于速度计算
        lastYaw: null,
        lastPitch: null,
        lastTimestamp: null,
        velocityHistory: [], // 历史速度（用于加速度）
      };
    }
    return $scope.spb360;
  }

  // 更新带宽模型（每次优化时调用）
  function updateBandwidthModel() {
    var state = getSharedState();
    var throughputMB = $scope.totalBandwidth / BIT2MB; // 转换为MB单位

    // 维护固定长度历史（例如100个样本）
    var history = state.bandwidthHistory;
    history.push(throughputMB);
    if (history.length > 100) history.shift();

    // 计算均值和方差（使用Welford在线算法）
    var mean = 0,
      m2 = 0,
      count = 0;
    for (var i = 0; i < history.length; i++) {
      count++;
      var delta = history[i] - mean;
      mean += delta / count;
      m2 += delta * (history[i] - mean);
    }
    state.bandwidthMean = mean;
    state.bandwidthVariance = count > 1 ? m2 / (count - 1) : 0.1;
  }

  // 更新运动模型
  function updateMotionModel(yaw, pitch) {
    var state = getSharedState();
    var now = Date.now() / 1000; // 秒

    if (
      state.lastYaw !== null &&
      state.lastPitch !== null &&
      state.lastTimestamp !== null
    ) {
      var dt = now - state.lastTimestamp;
      if (dt > 0.01) {
        // 避免dt过小
        var vx = (yaw - state.lastYaw) / dt;
        var vy = (pitch - state.lastPitch) / dt;
        state.velocityHistory.push({ vx: vx, vy: vy, t: now });

        // 保留最近100个速度点用于加速度计算
        if (state.velocityHistory.length > 100) state.velocityHistory.shift();

        // 计算加速度（速度差分）
        if (state.velocityHistory.length >= 2) {
          var accX = [],
            accY = [];
          for (var i = 1; i < state.velocityHistory.length; i++) {
            var v1 = state.velocityHistory[i - 1];
            var v2 = state.velocityHistory[i];
            var dt2 = v2.t - v1.t;
            if (dt2 > 0) {
              accX.push((v2.vx - v1.vx) / dt2);
              accY.push((v2.vy - v1.vy) / dt2);
            }
          }
          if (accX.length > 0) {
            // 计算均值
            var sumX = 0,
              sumY = 0;
            for (var j = 0; j < accX.length; j++) {
              sumX += accX[j];
              sumY += accY[j];
            }
            state.aXMean = sumX / accX.length;
            state.aYMean = sumY / accY.length;

            // 计算标准差
            var sqX = 0,
              sqY = 0;
            for (var j = 0; j < accX.length; j++) {
              sqX += Math.pow(accX[j] - state.aXMean, 2);
              sqY += Math.pow(accY[j] - state.aYMean, 2);
            }
            state.aXStd = Math.sqrt(sqX / accX.length);
            state.aYStd = Math.sqrt(sqY / accY.length);
          }
        }
      }
    }

    // 更新上次值
    state.lastYaw = yaw;
    state.lastPitch = pitch;
    state.lastTimestamp = now;
    state.motionHistory.push({ yaw: yaw, pitch: pitch, t: now });
    if (state.motionHistory.length > 100) state.motionHistory.shift();
  }

  // 计算预期卡顿时间 l_stall
  function computeLStall(
    k,
    l,
    yaw,
    pitch,
    bitrateHigh,
    bitrateLow,
    totalTiles,
    abrController
  ) {
    var state = getSharedState();

    // 获取当前EOV内的瓦片数量（通过get_visible_faces）
    var extensionAngle = (45 + k) * 2;
    var visibleFaces = $scope.get_visible_faces(
      yaw,
      pitch,
      true,
      extensionAngle
    );
    var visibleCount = Object.keys(visibleFaces).length;

    // 计算预计传输数据量 s_t (MB) = (高质量瓦片*高质量码率 + 低质量瓦片*低质量码率) * l / BIT2MB
    var s_t =
      ((visibleCount * bitrateHigh + (totalTiles - visibleCount) * bitrateLow) *
        l) /
      BIT2MB;
    s_t *= S_T_REDUNDANCY; // 冗余

    var b_t = $scope.players[0].getBufferLength(); // 缓冲区长度（秒），使用第一个播放器的缓冲区近似
    if (b_t <= 0) b_t = 0.1;

    var mean = state.bandwidthMean;
    var variance = state.bandwidthVariance;

    // 公式：l_stall = pre_num - post_num
    var pre_num = 0,
      post_num = 0;

    var arg1 = s_t / b_t - mean + variance;
    if (arg1 > 0) {
      pre_num =
        s_t *
        Math.exp(-mean + variance / 2) *
        normCDF(Math.log(arg1) / Math.sqrt(variance));
    }

    var arg2 = s_t / b_t - mean;
    if (arg2 > 0) {
      post_num = b_t * normCDF(Math.log(arg2) / Math.sqrt(variance));
    }

    return pre_num - post_num;
  }

  // 计算预期黑边比例 l_black
  function computeLBlack(k, l, yaw, pitch) {
    var state = getSharedState();

    // 使用当前速度（从最近两个视角计算）
    var vx = 0,
      vy = 0;
    if (state.motionHistory.length >= 2) {
      var last = state.motionHistory[state.motionHistory.length - 1];
      var prev = state.motionHistory[state.motionHistory.length - 2];
      var dt = last.t - prev.t;
      if (dt > 0) {
        vx = (last.yaw - prev.yaw) / dt;
        vy = (last.pitch - prev.pitch) / dt;
      }
    }

    // 位移分布（基于加速度模型）
    var d_x_mean = vx * l;
    var d_x_std = Math.sqrt((Math.pow(state.aXStd, 2) * Math.pow(l, 3)) / 3);
    var d_y_mean = vy * l;
    var d_y_std = Math.sqrt((Math.pow(state.aYStd, 2) * Math.pow(l, 3)) / 3);

    // 取绝对值用于判断
    var x_abs = Math.abs(d_x_mean);
    var y_abs = Math.abs(d_y_mean);

    var blackArea = 0;

    // 分支计算黑边面积（参考Python源码）
    if (x_abs <= k && y_abs <= k) {
      var p1 =
        normCDF((k - d_x_mean) / state.aXStd) *
        normCDF((k - d_y_mean) / state.aYStd);
      blackArea = 0 * p1;
    } else if (x_abs >= k && x_abs <= M + k && y_abs <= k) {
      var s2 = N * (x_abs - k);
      var p2 =
        (normCDF((M + k - d_x_mean) / state.aXStd) -
          normCDF((k - d_x_mean) / state.aXStd)) *
        normCDF((k - d_y_mean) / state.aYStd);
      blackArea = s2 * p2;
    } else if (x_abs <= k && y_abs >= k && y_abs <= N + k) {
      var s3 = M * (y_abs - k);
      var p3 =
        normCDF((k - d_x_mean) / state.aXStd) *
        (normCDF((N + k - d_y_mean) / state.aYStd) -
          normCDF((k - d_y_mean) / state.aYStd));
      blackArea = s3 * p3;
    } else if (x_abs >= k && x_abs <= M + k && y_abs >= k && y_abs <= N + k) {
      var s4 = M * N - (M + k - x_abs) * (N + k - y_abs);
      var p4 =
        (normCDF((M + k - d_x_mean) / state.aXStd) -
          normCDF((k - d_x_mean) / state.aXStd)) *
        (normCDF((N + k - d_y_mean) / state.aYStd) -
          normCDF((k - d_y_mean) / state.aYStd));
      blackArea = s4 * p4;
    } else {
      // 完全移出
      var p1 =
        normCDF((k - d_x_mean) / state.aXStd) *
        normCDF((k - d_y_mean) / state.aYStd);
      var p2 =
        (normCDF((M + k - d_x_mean) / state.aXStd) -
          normCDF((k - d_x_mean) / state.aXStd)) *
        normCDF((k - d_y_mean) / state.aYStd);
      var p3 =
        normCDF((k - d_x_mean) / state.aXStd) *
        (normCDF((N + k - d_y_mean) / state.aYStd) -
          normCDF((k - d_y_mean) / state.aYStd));
      var p4 =
        (normCDF((M + k - d_x_mean) / state.aXStd) -
          normCDF((k - d_x_mean) / state.aXStd)) *
        (normCDF((N + k - d_y_mean) / state.aYStd) -
          normCDF((k - d_y_mean) / state.aYStd));
      var p5 = 1 - p1 - p2 - p3 - p4;
      blackArea = M * N * p5;
    }

    return blackArea / (M * N); // 归一化
  }

  // 计算总代价 L = l_stall + eta * l_black
  function computeL(
    k,
    l,
    yaw,
    pitch,
    bitrateHigh,
    bitrateLow,
    totalTiles,
    abrController
  ) {
    var stall = computeLStall(
      k,
      l,
      yaw,
      pitch,
      bitrateHigh,
      bitrateLow,
      totalTiles,
      abrController
    );
    var black = computeLBlack(k, l, yaw, pitch);
    return stall + ETA * black;
  }

  // 网格搜索最优 (l, k)
  function optimize(
    yaw,
    pitch,
    bitrateHigh,
    bitrateLow,
    totalTiles,
    abrController
  ) {
    var state = getSharedState();
    var bestL = L_MIN;
    var bestK = K_MIN;
    var bestCost = Infinity;

    var lStep = (L_MAX - L_MIN) / (L_STEPS - 1);
    var kStep = (K_MAX - K_MIN) / (K_STEPS - 1);

    for (var i = 0; i < L_STEPS; i++) {
      var l = L_MIN + i * lStep;
      for (var j = 0; j < K_STEPS; j++) {
        var k = K_MIN + j * kStep;
        var cost = computeL(
          k,
          l,
          yaw,
          pitch,
          bitrateHigh,
          bitrateLow,
          totalTiles,
          abrController
        );
        if (cost < bestCost) {
          bestCost = cost;
          bestL = l;
          bestK = k;
        }
      }
    }

    // 更新共享状态
    state.bestL = bestL;
    state.bestK = bestK;
    // 计算当前最优k下的EOV内瓦片
    var extensionAngle = (45 + bestK) * 2;
    state.eovFaces = $scope.get_visible_faces(yaw, pitch, true, extensionAngle);

    return { l: bestL, k: bestK };
  }

  // 主决策函数
  function getMaxIndex(rulesContext) {
    const switchRequest = SwitchRequest(context).create();

    if (
      !rulesContext ||
      !rulesContext.hasOwnProperty("getMediaInfo") ||
      !rulesContext.hasOwnProperty("getAbrController")
    ) {
      return switchRequest;
    }

    const mediaType = rulesContext.getMediaInfo().type;
    const mediaInfo = rulesContext.getMediaInfo();
    const abrController = rulesContext.getAbrController();

    if (mediaType != "video") {
      return switchRequest;
    }

    var info = abrController.getSettings().info;
    var bufferLength = $scope.players[info.count].getBufferLength();
    if (bufferLength == 0) bufferLength = 0.1;

    // 预测未来视野中心（基于缓冲区长度）
    var predictedViewport = $scope.predict_center_viewport(
      bufferLength * $scope.videoFrameRate
    );
    let center_x = predictedViewport[0];
    let center_y = predictedViewport[1];

    // 运动模型和带宽模型的更新，每个视频片段只需要一次，由tile0进行
    if (info.count == 0) {
      // 更新运动模型
      updateMotionModel(center_x, center_y);

      // 更新带宽模型
      updateBandwidthModel();
    }

    // 获取码率列表
    const bitrateList = abrController.getBitrateList(mediaInfo);
    var highBitrate = bitrateList[bitrateList.length - 1].bitrate; // bps
    var lowBitrate = bitrateList[0].bitrate; // bps
    var totalTiles = $scope.players.length;

    var state = getSharedState();
    var now = Date.now();

    // 每隔5秒或首次调用时重新优化
    if (now - state.lastOptimizeTime > 5000 || state.lastOptimizeTime == 0) {
      optimize(
        center_x,
        center_y,
        highBitrate,
        lowBitrate,
        totalTiles,
        abrController
      );
      state.lastOptimizeTime = now;
    }

    // 判断当前瓦片是否在EOV内
    var inEOV = false;
    for (var face in state.eovFaces) {
      var faceIndex = parseInt(face.split("_")[2]);
      if (faceIndex == info.face) {
        inEOV = true;
        break;
      }
    }

    switchRequest.priority = SwitchRequest.PRIORITY.STRONG;
    switchRequest.quality = inEOV ? bitrateList.length - 1 : 0; // EOV内最高质量，外最低质量
    switchRequest.reason = "SPB360: 基于扩展视场优化";

    return switchRequest;
  }

  function setup() {}

  instance = {
    getMaxIndex: getMaxIndex,
  };

  setup();

  return instance;
}

SPB360RuleClass.__dashjs_factory_name = "SPB360Rule";
SPB360Rule = dashjs.FactoryMaker.getClassFactory(SPB360RuleClass);
