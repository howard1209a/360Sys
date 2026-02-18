//Viewport prediction_seconds Variables
const center_viewport_x = [];
const center_viewport_y = [];
const frame_array = [];

let cvp_x;
let cvp_y;

let lr_width;
let lr_height;

var new_width = undefined;
var new_height = undefined;

function update_center_viewport() {
  var frameObj = document.getElementById("frame");
  if (frameObj) {
    var scene = frameObj.contentWindow.document.querySelector("a-scene");
    var camera = scene.camera;
    var sky_sphere = scene.children[1]; //sky_sphere
    var sphere_mesh = sky_sphere.object3DMap.mesh;
  }

  if (camera && sphere_mesh) {
    const newRaycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(0, 0);

    newRaycaster.setFromCamera(mouse, camera);

    let intersection = [];

    //get the head position using raycast from the sphere to the camera
    sphere_mesh.raycast(newRaycaster, intersection);

    if (intersection.length > 0) {
      var cvp_x_norm = intersection[0].uv.x;
      var cvp_y_norm = intersection[0].uv.y;

      //values from -PI through +PI
      var cvp_x_radians = convert_normalized_to_radians(cvp_x_norm);
      var cvp_y_radians = convert_normalized_to_radians(cvp_y_norm);

      var frameObj = document.getElementById("frame");
      if (frameObj) {
        var appElement = document.querySelector(
          "[ng-controller=DashController]"
        );
        var $scope = angular.element(appElement).scope();
        if (!$scope.frameNumber) {
          requestAnimationFrame(update_center_viewport);
          return;
        }
        var currentFrame = $scope.frameNumber.get();
        const nb_samples_viewport = $scope.videoFrameRate;

        // 如果开启用户轨迹模拟，则用户轨迹视野角度要覆盖真实视野角度
        if ($scope.userTrackingData && $scope.userTrackingData.length > 0) {
          cvp_x_radians = $scope.user_tracking_viewport_x;
          cvp_y_radians = $scope.user_tracking_viewport_y;
        }

        // update the center_viewport variables for the linear regression prediction_seconds
        center_viewport_x.push(cvp_x_radians);
        center_viewport_y.push(cvp_y_radians);
        frame_array.push(currentFrame);

        if (frame_array.length > nb_samples_viewport) {
          center_viewport_x.shift();
          center_viewport_y.shift();
          frame_array.shift();
        }

        $scope.center_viewport_x = center_viewport_x;
        $scope.center_viewport_y = center_viewport_y;
        $scope.current_center_viewport_x = cvp_x_radians;
        $scope.current_center_viewport_y = cvp_y_radians;

        $scope.frame_array = frame_array;
      }

      requestAnimationFrame(update_center_viewport);
      return [cvp_x_radians, cvp_y_radians];
    }
  }

  requestAnimationFrame(update_center_viewport);
  return;
}
