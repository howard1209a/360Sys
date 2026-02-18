function updateUserTracking() {
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();

  if ($scope.userTrackingData && $scope.userTrackingData.length > 0) {
    var currentFrameIndex =
      $scope.frameNumber != 0 ? $scope.frameNumber.get() : 0;
    var userTrack = $scope.userTrackingData[currentFrameIndex + 1];
    var latitude = userTrack.latitude - 90;
    var longitude = -1 * userTrack.longitude + 180;
    // 旋转摄像机
    rotate(latitude, longitude);
  }

  requestAnimationFrame(updateUserTracking);
}

// 传入latitude纬度、longitude经度，对相机进行相应旋转
// 0 0 -> 正前方 90 0 -> 正上方 -90 0 -> 正下方 0 90 -> 左边 0 -90 右边 0 180 -> 正后方
function rotate(latitude, longitude) {
  var frameObj = document.getElementById("frame");
  var camera = frameObj.contentWindow.document.querySelector("#video_camera");

  latitude = -1 * latitude;
  longitude = -1 * longitude;

  var latitudeRad = (latitude * Math.PI) / 180;
  var longitudeRad = (longitude * Math.PI) / 180;

  var x = Math.cos(latitudeRad) * Math.cos(longitudeRad);
  var y = Math.cos(latitudeRad) * Math.sin(longitudeRad);
  var z = Math.sin(latitudeRad);

  var pitch = (Math.asin(z) * 180) / Math.PI;
  var yaw = (Math.atan2(y, x) * 180) / Math.PI;

  // Set the camera's rotation
  camera.setAttribute("rotation", `${pitch} ${yaw} 0`);

  // 更新实时模拟角度
  var appElement = document.querySelector("[ng-controller=DashController]");
  var $scope = angular.element(appElement).scope();
  $scope.user_tracking_viewport_x = (longitude * Math.PI) / 180;
  $scope.user_tracking_viewport_y = (latitude * Math.PI) / 90;
}
