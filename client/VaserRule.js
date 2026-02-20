var VaserRule;

function VaserRuleClass() {
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

    // 获取实时视野角度
    let center_viewport_x = $scope.current_center_viewport_x;
    let center_viewport_y = $scope.current_center_viewport_y;

    visible_faces = $scope.get_visible_faces(
      center_viewport_x,
      center_viewport_y,
      true,
      150
    );

    var in_fov = false;
    for (face in visible_faces) {
      var faceIndex = parseInt(face.split("_")[2]);
      if (faceIndex == info.face) {
        in_fov = true;
        break;
      }
    }

    switchRequest.quality = 0;
    switchRequest.reason = "Vaser算法：fov内传最高质量、fov外传次高质量";
    switchRequest.priority = SwitchRequest.PRIORITY.STRONG;

    const bitrateList = abrController.getBitrateList(mediaInfo);

    // fov内传最高质量、fov外传次高质量
    if (in_fov) {
      switchRequest.quality = bitrateList.length - 1;
    } else {
      switchRequest.quality = bitrateList.length - 2;
    }

    return switchRequest;
  }

  instance = {
    getMaxIndex: getMaxIndex,
  };

  setup();

  return instance;
}

VaserRuleClass.__dashjs_factory_name = "VaserRule";
VaserRule = dashjs.FactoryMaker.getClassFactory(VaserRuleClass);
