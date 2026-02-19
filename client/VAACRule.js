var VAACRule;

function VAACRuleClass() {
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

    // 获取预测视野角度
    var predictedViewport = $scope.predict_center_viewport(
      bufferLength * $scope.videoFrameRate
    );
    let center_viewport_x = predictedViewport[0];
    let center_viewport_y = predictedViewport[1];

    visible_faces = $scope.get_visible_faces(
      center_viewport_x,
      center_viewport_y,
      false,
      -1
    );

    var in_fov = false;
    for (face in visible_faces) {
      if (face.includes(info.face)) {
        in_fov = true;
        break;
      }
    }

    switchRequest.quality = 0;
    switchRequest.reason = "VAAC：视野内传最高质量、视野外传最低质量";
    switchRequest.priority = SwitchRequest.PRIORITY.STRONG;

    const bitrateList = abrController.getBitrateList(mediaInfo);

    // 视野内传最高质量、视野外传最低质量
    if (in_fov) {
      switchRequest.quality = bitrateList.length - 1;
    } else {
      switchRequest.quality = 0;
    }

    return switchRequest;
  }

  instance = {
    getMaxIndex: getMaxIndex,
  };

  setup();

  return instance;
}

VAACRuleClass.__dashjs_factory_name = "VAACRule";
VAACRule = dashjs.FactoryMaker.getClassFactory(VAACRuleClass);
