var PWRule;

function PWRuleClass() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();
  let factory = dashjs.FactoryMaker;
  let SwitchRequest = factory.getClassFactoryByName("SwitchRequest");
  let context = this.context;
  let instance;

  function setup() {}

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
    if (bufferLength == 0) {
      // 兜底buffer长度为0的情况
      bufferLength = 0.1;
    }

    var availableBit = $scope.totalBandwidth * bufferLength;
    const bitrateList = abrController.getBitrateList(mediaInfo);

    // 获取预测视野角度
    var predictedViewport = $scope.predict_center_viewport(
      bufferLength * $scope.videoFrameRate
    );
    let center_viewport_x = predictedViewport[0];
    let center_viewport_y = predictedViewport[1];

    var visible_faces = $scope.get_visible_faces(
      center_viewport_x,
      center_viewport_y,
      false,
      -1
    );

    var visible_face_count = Object.keys(visible_faces).length;
    var highBitrateSet = new Set();
    var lowBitrateSet = new Set();
    var highBitrate = bitrateList[bitrateList.length - 1].bitrate;
    var lowBitrate = bitrateList[bitrateList.length - 2].bitrate;
    var in_fov_tile_list = [];
    var out_fov_tile_list = [];
    availableBit -= visible_face_count * lowBitrate * 5;
    for (let i = 0; i < $scope.players.length; i++) {
      var tile_in_fov = false;
      for (face in visible_faces) {
        var faceIndex = parseInt(face.split("_")[2]);
        if (faceIndex == i) {
          tile_in_fov = true;
          break;
        }
      }
      if (tile_in_fov) {
        lowBitrateSet.add(i);
        in_fov_tile_list.push(i);
      } else {
        out_fov_tile_list.push(i);
      }
    }

    if (availableBit <= 0) {
      switchRequest.priority = SwitchRequest.PRIORITY.STRONG;
      switchRequest.quality = getQuality(
        highBitrateSet,
        lowBitrateSet,
        info.face,
        bitrateList
      );
      return switchRequest;
    }

    for (var i = 0; i < in_fov_tile_list.length; i++) {
      var tile_index = in_fov_tile_list[i];
      lowBitrateSet.delete(tile_index);
      highBitrateSet.add(tile_index);
      availableBit -= (highBitrate - lowBitrate) * 5;
      if (availableBit <= 0) {
        switchRequest.priority = SwitchRequest.PRIORITY.STRONG;
        switchRequest.quality = getQuality(
          highBitrateSet,
          lowBitrateSet,
          info.face,
          bitrateList
        );
        return switchRequest;
      }
    }

    for (var i = 0; i < out_fov_tile_list.length; i++) {
      var tile_index = out_fov_tile_list[i];
      highBitrateSet.add(tile_index);
      availableBit -= highBitrate * 5;
      if (availableBit <= 0) {
        switchRequest.priority = SwitchRequest.PRIORITY.STRONG;
        switchRequest.quality = getQuality(
          highBitrateSet,
          lowBitrateSet,
          info.face,
          bitrateList
        );
        return switchRequest;
      }
    }

    switchRequest.priority = SwitchRequest.PRIORITY.STRONG;
    switchRequest.quality = getQuality(
      highBitrateSet,
      lowBitrateSet,
      info.face,
      bitrateList
    );
    return switchRequest;
  }

  function getQuality(highBitrateSet, lowBitrateSet, tile_index, bitrateList) {
    if (highBitrateSet.has(tile_index)) {
      return bitrateList.length - 1;
    }
    if (lowBitrateSet.has(tile_index)) {
      return bitrateList.length - 2;
    }
    return 0;
  }

  instance = {
    getMaxIndex: getMaxIndex,
  };

  setup();

  return instance;
}

PWRuleClass.__dashjs_factory_name = "PWRule";
PWRule = dashjs.FactoryMaker.getClassFactory(PWRuleClass);
