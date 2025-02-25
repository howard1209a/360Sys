var sphere_reference, camera_reference;

function dynamicEditClass() {
  [sphere_reference, camera_reference] = getIframeEntities("frame");

  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  if ($scope.frameNumber == 0) {
    if (!camera_reference.videoFrames) {
      requestAnimationFrame(dynamicEditClass);
      return;
    }
    $scope.frameNumber = camera_reference.videoFrames["video_0"];
    $scope.videoFrameRate =
      camera_reference.videoFrames["video_0"]["frameRate"];
  }
  requestAnimationFrame(dynamicEditClass);
}

function getIframeEntities(frameId) {
  var frameObj = document.getElementById(frameId);
  if (frameObj) {
    var camera_reference =
      frameObj.contentWindow.document.querySelector("#video_camera");
    var sphere_reference =
      frameObj.contentWindow.document.querySelector("#sky-sphere");
    return [sphere_reference, camera_reference];
  }
  return;
}

// 0 1 映射 -180 180
function convert_normalized_to_degree(cvp_norm) {
  return 360 * cvp_norm - 180;
}

// 0 1 映射 -pi pi
function convert_normalized_to_radians(cvp_norm) {
  return 2 * Math.PI * cvp_norm - Math.PI;
}
