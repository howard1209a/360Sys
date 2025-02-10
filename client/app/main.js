var app = angular.module("myapp", ["ngRoute"]);

app.config(function ($routeProvider, $locationProvider) {
  $routeProvider
    .when("/", {
      templateUrl: "pages/home.html",
      controller: "HomeController",
    })
    .when("/about", {
      templateUrl: "pages/about.html",
      controller: "AboutController",
    })
    .when("/contact", {
      templateUrl: "pages/contact.html",
      controller: "ContactController",
    })
    .when("/player", {
      templateUrl: "pages/player.html",
      controller: "DashController",
    });
});

app.controller("HomeController", function ($scope) {
  $scope.message = "Routing pages with ngRoute is damn awesome!";
});

app.controller("AboutController", function ($scope) {
  $scope.message = "You can see more about ngRoute in the oficial website.";
});

app.controller("ContactController", function ($scope) {
  $scope.message = "No. :P";
});

app.controller("DashController", [
  "$scope",
  "$interval",
  function ($scope, $interval) {
    $scope.players = [];
    $scope.playerCount = 0; // 播放器总个数
    $scope.videoFrameRate = 0; // aframe摄像机的帧率，默认60
    $scope.frameNumber = 0; // 单帧信息
    $scope.buffer_empty_flag = []; // 播放器是否卡顿标记符
    ($scope.lon = 90), ($scope.lat = 0); // 经纬度
    $scope.contents = {}; // JSON配置

    $scope.player_ready = 0; // video原生标签帧序列就绪的播放器个数
    $scope.json_output = []; // 输出文件信息
    $scope.download_started = false; // 标记是否已开始下载输出文件

    $scope.normalizedTime = 0; // 设置所有播放器最新的时间为标准时间
    $scope.totalThroughput = 0; // 视频数据下载吞吐量，每秒更新一次
    $scope.playerBufferLength = []; // todo delete
    $scope.playerAverageThroughput = []; // todo delete
    $scope.playerTime = []; // todo delete
    $scope.playerDownloadingQuality = []; // todo delete
    $scope.playerFOVScore = []; // todo delete
    $scope.playerContentScore = []; // todo delete
    $scope.playerPastDownloadingQuality = []; // todo delete
    $scope.playerCatchUp = []; // todo delete
    $scope.playerDivation = []; // todo delete

    $scope.playerBitrateList = []; // todo delete
    $scope.requestList = []; // 由dash内部注入，保存了全部播放器的http请求，按照请求结束下载时间从小到大排序

    $scope.selectedItem = {
      // 默认视频源
      type: "json",
      value: "https://10.29.160.99/360sys/client/default.json",
    };
    $scope.optionButton = "Show Options";
    $scope.selectedRule = "FOVRule";

    $scope.requestDuration = 3000; // 计算吞吐量的区间长度
    $scope.IntervalOfComputetotalThroughput = 1000; // 计算吞吐量的时间间隔

    $scope.playerBufferToKeep = 3; // 未知作用配置
    $scope.playerStableBufferTime = 3; // dash的buffer控制参数，参照https://ki8trbsdgd.feishu.cn/wiki/W5Jww02i3ijgz1kjQltcvYWUnlh?fromScene=spaceOverview
    $scope.playerBufferTimeAtTopQuality = 3; // dash的buffer控制参数，参照https://ki8trbsdgd.feishu.cn/wiki/W5Jww02i3ijgz1kjQltcvYWUnlh?fromScene=spaceOverview
    $scope.playerMinDrift = 0.02; // dash的buffer控制参数，参照https://ki8trbsdgd.feishu.cn/wiki/W5Jww02i3ijgz1kjQltcvYWUnlh?fromScene=spaceOverview

    $scope.availableStreams = [
      // 预设资源链接
      {
        name: "LVOD",
        json: "http://localhost/CMPVP907/aframeVP907.json",
      },
      {
        name: "SVOD",
        json: "http://115.156.159.94:8800/CMPVP907/aframeVP907.json",
      },
      {
        name: "LIVE",
        json: "http://222.20.77.111/dash/default.json",
      },
      {
        name: "BUNNY",
        url: "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd",
      },
    ];
    // abr策略列表
    $scope.rules = [
      "FOVRule",
      "HighestBitrateRule",
      "LowestBitrateRule",
      "FOVEditRule",
      "DefaultRule",
    ];

    $scope.center_viewport_x = []; // 视野经度列表，值为-pi到pi，实际范围360度，长度为aframe摄像机的帧率
    $scope.center_viewport_y = []; // 视野纬度列表，值为-pi到pi，实际范围180度，长度为aframe摄像机的帧率
    $scope.frame_array = []; // 帧序号列表，长度为aframe摄像机的帧率
    $scope.current_center_viewport_x = 0; // 实时视野经度，值为-pi到pi
    $scope.current_center_viewport_y = 0; // 实时视野纬度，值为-pi到pi
    $scope.yaw = 0; // 同current_center_viewport_x
    $scope.pitch = 0; // 同current_center_viewport_y
    $scope.hasEditScheduledValue = false; // edit机制相关
    $scope.editHappenedValue = false; // edit机制相关
    $scope.radiansRotationValue = 0; // edit机制相关
    $scope.editTypeValue = "null"; // edit机制相关

    // 基于最近1s内的视野数据，使用线性回归/脊回归算法预测prediction_frame帧之后的用户视野角度，该方式只适用于短期预测
    $scope.predict_center_viewport = function (
      prediction_frame,
      ridge = false
    ) {
      function linear_function(a, b, x) {
        return a * x + b;
      }

      function linearRegression(y, x) {
        var lr = {};
        var n = y.length;
        var sum_x = 0;
        var sum_y = 0;
        var sum_xy = 0;
        var sum_xx = 0;
        var sum_yy = 0;
        var lambda = 0;

        for (var i = 0; i < y.length; i++) {
          sum_x += x[i];
          sum_y += y[i];
          sum_xy += x[i] * y[i];
          sum_xx += x[i] * x[i];
          sum_yy += y[i] * y[i];
        }

        if (ridge) {
          // Using a lambda that will always be 5% of the sum_xx variable so it can follow the expression
          // when it increases its values;
          lambda = sum_xx * 0.05;
        }
        lr["slope"] =
          (n * sum_xy - sum_x * sum_y) /
          (n * (sum_xx + lambda) - sum_x * sum_x);
        lr["intercept"] =
          ((sum_xx + lambda) * sum_y - sum_x * sum_xy) /
          (n * (sum_xx + lambda) - sum_x * sum_x);
        return lr;
      }

      function convert_normalized_to_radians(cvp_norm) {
        return 2 * Math.PI * cvp_norm - Math.PI;
      }

      function convert_radians_to_normalized_from_array(cvp_radians) {
        return cvp_radians.map((cvp) => cvp / (2 * Math.PI) + 0.5);
      }

      if ($scope.frame_array.length < $scope.videoFrameRate) return;

      lr_width = linearRegression(
        convert_radians_to_normalized_from_array($scope.center_viewport_x),
        $scope.frame_array
      );

      lr_height = linearRegression(
        convert_radians_to_normalized_from_array($scope.center_viewport_y),
        $scope.frame_array
      );

      new_yaw = linear_function(
        lr_width.slope,
        lr_width.intercept,
        $scope.frame_array[$scope.frame_array.length - 1] + prediction_frame
      );
      new_pitch = linear_function(
        lr_height.slope,
        lr_height.intercept,
        $scope.frame_array[$scope.frame_array.length - 1] + prediction_frame
      );

      new_yaw = convert_normalized_to_radians(new_yaw);
      new_pitch = convert_normalized_to_radians(new_pitch);

      if (new_yaw > Math.PI) {
        new_yaw = -Math.PI + (new_yaw % Math.PI);
      } else if (new_yaw < -Math.PI) {
        new_yaw = Math.PI + (new_yaw % Math.PI);
      }

      if (new_pitch > Math.PI) {
        new_pitch = new_pitch - Math.floor(new_pitch / Math.PI) * Math.PI;
      } else if (new_pitch < -Math.PI) {
        new_pitch = new_pitch + Math.floor(new_pitch / Math.PI) * Math.PI;
      }

      return [new_yaw, new_pitch];
    };

    // 传入经纬度角，返回每个面位于视锥体内点的比例
    $scope.get_visible_faces = function (cvp_x_radians, cvp_y_radians) {
      var frameObj = document.getElementById("frame");
      var scene = frameObj.contentWindow.document.querySelector("a-scene");
      var camera = scene.camera;
      var camera_reference = scene.children[2];
      let faceStructureModified = camera_reference.faceStructure;
      var visibleObjects = {};

      if (camera && faceStructureModified) {
        camera.updateMatrix();
        camera.updateMatrixWorld();

        //Copy the actual camera to simulate rotations so that the original camera is not influenced
        var cameraAux = camera.clone();

        var frustum = new THREE.Frustum();

        // Make a frustum to know what is in the camera vision
        frustum.setFromProjectionMatrix(
          new THREE.Matrix4().multiplyMatrices(
            camera.projectionMatrix,
            camera.matrixWorldInverse
          )
        );

        // Uses the faceStructureModified value because it could have an edit on the playback
        for (var face in faceStructureModified) {
          let countPointsVisible = 0;
          let numberPoints = faceStructureModified[face].length;
          for (var position = 0; position < numberPoints; position++)
            if (frustum.containsPoint(faceStructureModified[face][position]))
              countPointsVisible++;

          if (countPointsVisible > 0) {
            let numberTruncaded =
              Math.floor((countPointsVisible / numberPoints) * 1000) / 1000;
            visibleObjects[face] = numberTruncaded;
          }
        }

        // Use quaternion to simulate the camera rotation
        // It was noticed that the camera object does not change its quaternion value after the render process.
        // With that in mind, the simulation is done by rotating the camera to the given center of the viewport
        // as if the camera was in the initial position.
        const quaternion_x = new THREE.Quaternion();
        const quaternion_y = new THREE.Quaternion();

        // Multiply by -1 because the quaternion rotation reference is the oposite from the one received from the update_center_viewport() function
        quaternion_x.setFromAxisAngle(
          new THREE.Vector3(0, 1, 0),
          -1 * cvp_x_radians
        );

        // Divide the Y center of the viewport because it goes from -PI to +PI and the rotation goes from -PI/2 to +PI/2 in this axis
        quaternion_y.setFromAxisAngle(
          new THREE.Vector3(1, 0, 0),
          cvp_y_radians / 2
        );

        //Just to make sure that its start from the initial position
        cameraAux.quaternion = new THREE.Quaternion(0, 0, 0, 1);
        cameraAux.quaternion.multiply(quaternion_x).multiply(quaternion_y);

        cameraAux.updateMatrix();
        cameraAux.updateMatrixWorld();

        // Make a new frustum to know what is in the camera vision simulation
        var frustum2 = new THREE.Frustum();

        frustum2.setFromProjectionMatrix(
          new THREE.Matrix4().multiplyMatrices(
            cameraAux.projectionMatrix,
            cameraAux.matrixWorldInverse
          )
        );

        visibleObjects = {};

        //Uses the faceStructure object because the value is not updaded on the render
        for (var face in faceStructure) {
          let countPointsVisible = 0;
          let numberPoints = faceStructure[face].length;
          for (var position = 0; position < numberPoints; position++)
            if (frustum2.containsPoint(faceStructure[face][position]))
              countPointsVisible++;

          if (countPointsVisible > 0) {
            let numberTruncaded =
              Math.floor((countPointsVisible / numberPoints) * 1000) / 1000;
            visibleObjects[face] = numberTruncaded;
          }
        }
      }
      return visibleObjects;
    };

    $scope.changeStream = function () {
      console.log($scope.selectedItem.value.slice(-4));
      if (
        $scope.selectedItem.value.length > 5 &&
        $scope.selectedItem.value.slice(-4) == "json"
      ) {
        $scope.selectedItem.type = "json";
      } else {
        $scope.selectedItem.type = "url";
      }
    };

    // For setting up the ABR rule
    $scope.showoption = function () {
      if ($scope.optionButton == "Show Options") {
        document.getElementById("option").style =
          "background-color: #e2e1e4; z-index: 1000; position: absolute;";
        $scope.optionButton = "Hide Options";
      } else {
        document.getElementById("option").style = "display: none;";
        $scope.optionButton = "Show Options";
      }
    };

    $scope.changeABRStrategy = function (strategy) {
      for (let i = 0; i < $scope.rules.length; i++) {
        let d = document.getElementById($scope.rules[i]);
        d.checked = false;
      }
      document.getElementById(strategy).checked = true;
      $scope.selectedRule = strategy;
    };

    // get请求url并设置回调
    function getContents(url, callback) {
      var xhr = new XMLHttpRequest();

      xhr.open("GET", url, true);

      xhr.onload = callback;
      xhr.send();
    }

    // 解析JSON文件
    $scope.openJSON = function (url) {
      $scope.players = [];
      $scope.buffer_empty_flag = [];
      $scope.playerCount = 0;
      $scope.lon = 90;
      $scope.lat = 0;
      $scope.contents = {};
      getContents(url, function () {
        $scope.contents = JSON.parse(this.responseText);
        if ($scope.contents.edits) {
          console.log($scope.contents.edits);
        }
        document.getElementById("Link").style = "display: none;";
        document.getElementById("Render").style = "display: inline;";
      });
    };

    // Read default json file if json is unavailable, then change the srcs
    $scope.openURLs = function (url) {
      $scope.contents = {};
      getContents("./default.json", function () {
        $scope.contents = JSON.parse(this.responseText);
        let urls = url.split(/[(\n)\n]+/);
        for (let i = 0; i < $scope.contents.face; i++) {
          for (let j = 0; j < $scope.contents.row; j++) {
            for (let k = 0; k < $scope.contents.col; k++) {
              $scope.contents.tiles[i][j][k].src =
                i * $scope.contents.row * $scope.contents.col +
                  j * $scope.contents.col +
                  k <
                urls.length
                  ? urls[
                      i * $scope.contents.row * $scope.contents.col +
                        j * $scope.contents.col +
                        k
                    ]
                  : urls[urls.length - 1];
            }
          }
        }
        document.getElementById("Link").style = "display: none;";
        document.getElementById("Render").style = "display: inline;";
      });
    };

    // 点击Render后执行，加载播放器html
    $scope.aframe_init = function () {
      if ($scope.contents == {}) {
        return;
      }
      document.getElementById("frame").src =
        "./pages/" +
        $scope.contents.face +
        "_" +
        $scope.contents.row +
        "_" +
        $scope.contents.col +
        ".html";
      $scope.lon = 90;
      $scope.lat = 0;
      document.getElementById("Render").style = "display: none;";
      document.getElementById("Load").style = "display: inline;";
    };

    // 暂停全部播放器
    $scope.pause_all = function () {
      for (let i = 0; i < $scope.playerCount; i++) {
        $scope.players[i].pause();
        console.log("Player_" + i + " pauses.");
      }
      if ($scope.contents.audio && $scope.contents.audio != "") {
        $scope.players[$scope.playerCount].pause();
        console.log("Audio pauses.");
      }
      document.getElementById("Pause").style = "display: none;";
      document.getElementById("Play").style = "display: inline;";
    };

    // 播放全部播放器
    $scope.play_all = function () {
      for (let i = 0; i < $scope.playerCount; i++) {
        $scope.players[i].play();
        console.log("Player_" + i + " plays.");
      }
      if ($scope.contents.audio && $scope.contents.audio != "") {
        $scope.players[$scope.playerCount].play();
        console.log("Audio plays.");
      }
      document.getElementById("Play").style = "display: none;";
      document.getElementById("Pause").style = "display: inline;";
    };

    // 任意播放器卡顿时触发，主动暂停全部播放器
    function buffer_empty_event(e) {
      $scope.buffer_empty_flag[e.info.count] = true;
      // $scope.pause_all();
    }

    // 任意播放器卡顿后重新加载完成时触发，当全部播放器帧就绪时主动播放全部播放器
    function buffer_loaded_event(e) {
      if ($scope.buffer_empty_flag[e.info.count] == true) {
        $scope.buffer_empty_flag[e.info.count] = false;
        for (let i = 0; i < $scope.playerCount; i++) {
          if ($scope.buffer_empty_flag[i] == true) {
            return;
          }
        }
        if (
          $scope.contents.audio &&
          $scope.contents.audio != "" &&
          $scope.buffer_empty_flag[$scope.playerCount] == true
        ) {
          return;
        }
        console.log("$scope.player_ready: ", $scope.player_ready);
        if ($scope.player_ready >= 6) {
          $scope.play_all();
        }
      }
    }

    // video原生标签解码帧序列就绪时触发，当全部播放器帧就绪时主动播放全部播放器
    function can_play_event(e) {
      $scope.player_ready++;
      if ($scope.player_ready >= 6) {
        console.log("PLAY");
        $scope.play_all();
      }
    }

    // 下载csv
    function download_csv() {
      console.log("END OF PLAYBACK REACHED!!");
      console.log("DOWNLOAD CSV WAS TRIGGERED!!!");
      console.log("$scope.json_output: ", $scope.json_output);
      var json_pre = $scope.json_output;
      var json = json_pre;
      console.log("downloading CSV...");
      var csv = JSON2CSV(json, true);
      var downloadLink = document.createElement("a");
      var blob = new Blob(["\ufeff", csv]);
      var url = URL.createObjectURL(blob);

      downloadLink.id = "download_csv";
      downloadLink.href = url;
      downloadLink.download = "data.csv";

      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);

      $scope.download_started = true;

      function JSON2CSV(objArray, header = false) {
        var array =
          typeof objArray != "object" ? JSON.parse(objArray) : objArray;
        var str = "";
        var line = "";

        if (header) {
          head = objArray[0];
          for (var key in head) {
            str += key + ",";
          }
          str = str.slice(0, -1);
          str += "\r\n";
        }

        if ($("#labels").is(":checked")) {
          var head = array[0];
          if ($("#quote").is(":checked")) {
            for (var index in array[0]) {
              var value = index + "";
              line += '"' + value.replace(/"/g, '""') + '",';
            }
          } else {
            for (var index in array[0]) {
              line += index + ",";
            }
          }

          line = line.slice(0, -1);
          str += line + "\r\n";
        }

        for (var i = 0; i < array.length; i++) {
          var line = "";

          if ($("#quote").is(":checked")) {
            for (var index in array[i]) {
              var value = array[i][index] + "";
              line += '"' + value.replace(/"/g, '""') + '",';
            }
          } else {
            for (var index in array[i]) {
              line += array[i][index] + ",";
            }
          }

          line = line.slice(0, -1);
          download_csv;
          str += line + "\r\n";
        }
        return str;
      }
    }

    $scope.download_csv = download_csv;

    // 点击Load时执行
    $scope.initial = function () {
      let video, url;

      // Video part
      for (let i = 0; i < $scope.contents.face; i++) {
        for (let j = 0; j < $scope.contents.row; j++) {
          for (let k = 0; k < $scope.contents.col; k++) {
            video = document
              .getElementById("frame")
              .contentWindow.document.querySelector(
                "#" +
                  "video_" +
                  [
                    i * $scope.contents.row * $scope.contents.col +
                      j * $scope.contents.col +
                      k,
                  ]
              );

            // 每个瓦片创建一个dash播放器
            $scope.players[$scope.playerCount] =
              new dashjs.MediaPlayer().create();
            url = $scope.contents.baseUrl + $scope.contents.tiles[i][j][k].src;
            $scope.buffer_empty_flag[$scope.playerCount] = true;

            // 为dash播放器添加一些自定义配置参数
            $scope.players[$scope.playerCount].updateSettings({
              info: {
                // 添加一些特定数据绑定，dash回调中也可以查看这些info
                id:
                  "video_" +
                  [
                    i * $scope.contents.row * $scope.contents.col +
                      j * $scope.contents.col +
                      k,
                  ],
                count: $scope.playerCount,
                face: i,
                row: j,
                col: k,
                duration: $scope.contents.duration,
                width: $scope.contents.tiles[i][j][k].width,
                height: $scope.contents.tiles[i][j][k].height,
                location: {
                  x: $scope.contents.tiles[i][j][k].x,
                  y: $scope.contents.tiles[i][j][k].y,
                  z: $scope.contents.tiles[i][j][k].z,
                },
                rotation: {
                  rx: $scope.contents.tiles[i][j][k].rx,
                  ry: $scope.contents.tiles[i][j][k].ry,
                  rz: $scope.contents.tiles[i][j][k].rz,
                },
                totalThroughputNeeded: true,
              },
              streaming: {
                abr: {
                  useDefaultABRRules: false,
                },
                buffer: {
                  bufferToKeep: $scope.playerBufferToKeep,
                  stableBufferTime: $scope.playerStableBufferTime,
                  bufferTimeAtTopQuality: $scope.playerBufferTimeAtTopQuality,
                  fastSwitchEnabled: true,
                },
                delay: {
                  liveDelay: 0,
                },
                liveCatchup: {
                  enabled: true,
                  minDrift: $scope.playerMinDrift,
                },
              },
            });

            // 添加自定义abr算法
            switch ($scope.selectedRule) {
              case "FOVRule":
                $scope.players[$scope.playerCount].addABRCustomRule(
                  "qualitySwitchRules",
                  "FOVRule",
                  FOVRule
                );
                break;
              case "HighestBitrateRule":
                $scope.players[$scope.playerCount].addABRCustomRule(
                  "qualitySwitchRules",
                  "HighestBitrateRule",
                  HighestBitrateRule
                );
                break;
              case "LowestBitrateRule":
                $scope.players[$scope.playerCount].addABRCustomRule(
                  "qualitySwitchRules",
                  "LowestBitrateRule",
                  LowestBitrateRule
                );
                break;
              case "FOVEditRule":
                $scope.players[$scope.playerCount].addABRCustomRule(
                  "qualitySwitchRules",
                  "FOVEditRule",
                  FOVEditRule
                );
                break;
              default:
                $scope.players[$scope.playerCount].updateSettings({
                  streaming: {
                    abr: {
                      useDefaultABRRules: true,
                    },
                  },
                });
                break;
            }

            // 注册事件监听与回调函数
            $scope.players[$scope.playerCount].on(
              dashjs.MediaPlayer.events["BUFFER_EMPTY"],
              buffer_empty_event
            );
            $scope.players[$scope.playerCount].on(
              dashjs.MediaPlayer.events["BUFFER_LOADED"],
              buffer_loaded_event
            );

            $scope.players[$scope.playerCount].on(
              dashjs.MediaPlayer.events["CAN_PLAY"],
              can_play_event
            );
            $scope.players[$scope.playerCount].on(
              dashjs.MediaPlayer.events["PLAYBACK_ENDED"],
              download_csv
            );

            // 初始化一些变量
            $scope.players[$scope.playerCount].initialize(video, url, false);
            $scope.playerBufferLength[$scope.playerCount] =
              $scope.players[$scope.playerCount].getBufferLength();
            $scope.playerAverageThroughput[$scope.playerCount] =
              $scope.players[$scope.playerCount].getAverageThroughput("video");
            $scope.playerTime[$scope.playerCount] =
              $scope.players[$scope.playerCount].time();
            $scope.playerDownloadingQuality[$scope.playerCount] =
              $scope.players[$scope.playerCount].getQualityFor("video");
            $scope.playerFOVScore[$scope.playerCount] = NaN;
            $scope.playerContentScore[$scope.playerCount] = NaN;
            $scope.playerBitrateList[$scope.playerCount] = [];
            $scope.playerCatchUp[$scope.playerCount] = false;

            $scope.playerCount++;
          }
        }
      }

      // todo delete
      if ($scope.contents.audio && $scope.contents.audio != "") {
        var audio = document
          .getElementById("frame")
          .contentWindow.document.querySelector("#audio");
        $scope.players[$scope.playerCount] = new dashjs.MediaPlayer().create();
        url = $scope.contents.baseUrl + $scope.contents.audio;
        $scope.buffer_empty_flag[$scope.playerCount] = true;

        $scope.players[$scope.playerCount].updateSettings({
          info: {
            id: "audio",
            count: $scope.playerCount,
            duration: $scope.contents.duration,
          },
          //   'debug': {
          //     'logLevel': dashjs.Debug.LOG_LEVEL_DEBUG
          // }
        });

        // Turn on the event listeners and add actions for triggers
        $scope.players[$scope.playerCount].on(
          dashjs.MediaPlayer.events["BUFFER_EMPTY"],
          buffer_empty_event
        );
        $scope.players[$scope.playerCount].on(
          dashjs.MediaPlayer.events["BUFFER_LOADED"],
          buffer_loaded_event
        );

        // Initializing
        $scope.players[$scope.playerCount].initialize(audio, url, false);
        $scope.playerBufferLength[$scope.playerCount] =
          $scope.players[$scope.playerCount].getBufferLength();
        $scope.playerAverageThroughput[$scope.playerCount] =
          $scope.players[$scope.playerCount].getAverageThroughput("audio");
        $scope.playerTime[$scope.playerCount] =
          $scope.players[$scope.playerCount].time();
        $scope.playerDownloadingQuality[$scope.playerCount] =
          $scope.players[$scope.playerCount].getQualityFor("audio");
        $scope.playerCatchUp[$scope.playerCount] = false;
      }

      // aframe每渲染一帧执行一次，设置标准时间为所有播放器最快时间
      requestAnimationFrame(setNormalizedTime);
      // 每隔一段时间计算一次吞吐量
      setInterval(
        computetotalThroughput,
        $scope.IntervalOfComputetotalThroughput
      );
      requestAnimationFrame(dynamicEditClass);
      // aframe每渲染一帧执行一次，更新用户视野
      requestAnimationFrame(update_center_viewport);
      // aframe每渲染一帧执行一次，更新输出csv文件
      // requestAnimationFrame(updateOutputFileInFrame);
      setInterval(updateOutputFileInTime, 1000);

      initChart();

      document.getElementById("Load").style = "display: none;";
      document.getElementById("Play").style = "display: inline;";
    };

    function formatTimestamp(timestamp) {
      const date = new Date(timestamp * 1000); // 将时间戳转为毫秒级别
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0"); // 月份从0开始，所以需要加1
      const day = String(date.getDate()).padStart(2, "0");
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");
      const seconds = String(date.getSeconds()).padStart(2, "0");

      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }

    function updateOutputFileInTime() {
      let numPlayer = $scope.players.length;
      let stringListQuality = "[";
      let predicted_visible_faces = $scope.get_visible_faces(
        $scope.yaw,
        $scope.pitch
      );
      for (let i = 0; i < numPlayer - 1; i++)
        stringListQuality += $scope.players[i].getQualityFor("video") + ";";

      stringListQuality = stringListQuality.slice(
        0,
        stringListQuality.length - 1
      );
      stringListQuality += "]";

      visibleFaces = "[";
      percentageVisibleFaces = "[";
      for (face in predicted_visible_faces) {
        visibleFaces += face.slice(-1) + ";";
        percentageVisibleFaces += predicted_visible_faces[face] + ";";
      }

      visibleFaces = visibleFaces.slice(0, visibleFaces.length - 1);
      visibleFaces += "]";

      percentageVisibleFaces = percentageVisibleFaces.slice(
        0,
        percentageVisibleFaces.length - 1
      );
      percentageVisibleFaces += "]";

      let frame_data = {
        timeStamp: formatTimestamp(Math.floor(Date.now() / 1000)),
        totalThroughput: $scope.totalThroughput,
        listQuality: stringListQuality,
        visibleFaces: visibleFaces,
        percentageVisibleFaces: percentageVisibleFaces,
        yaw: Number.parseFloat($scope.yaw).toFixed(4),
        pitch: Number.parseFloat($scope.pitch).toFixed(4),
      };

      $scope.json_output.push(frame_data);
    }

    // 更新输出指标;
    function updateOutputFileInFrame() {
      let numPlayer = $scope.players.length;
      let stringListQuality = "[";
      let predicted_visible_faces = $scope.get_visible_faces(
        $scope.yaw,
        $scope.pitch
      );
      for (let i = 0; i < numPlayer - 1; i++)
        stringListQuality += $scope.players[i].getQualityFor("video") + ";";

      stringListQuality = stringListQuality.slice(
        0,
        stringListQuality.length - 1
      );
      stringListQuality += "]";

      visibleFaces = "[";
      percentageVisibleFaces = "[";
      for (face in predicted_visible_faces) {
        visibleFaces += face.slice(-1) + ";";
        percentageVisibleFaces += predicted_visible_faces[face] + ";";
      }

      visibleFaces = visibleFaces.slice(0, visibleFaces.length - 1);
      visibleFaces += "]";

      percentageVisibleFaces = percentageVisibleFaces.slice(
        0,
        percentageVisibleFaces.length - 1
      );
      percentageVisibleFaces += "]";

      let frame_data = {
        frame: $scope.frameNumber != 0 ? $scope.frameNumber.get() : 0,
        totalThroughput: $scope.totalThroughput,
        listQuality: stringListQuality,
        visibleFaces: visibleFaces,
        percentageVisibleFaces: percentageVisibleFaces,
        yaw: Number.parseFloat($scope.yaw).toFixed(4),
        pitch: Number.parseFloat($scope.pitch).toFixed(4),
        hasEditScheduled: $scope.hasEditScheduledValue,
        editHappened: $scope.editHappenedValue,
        radiansRotation: Number.parseFloat($scope.radiansRotationValue).toFixed(
          4
        ),
        editType: $scope.editTypeValue,
      };

      $scope.json_output.push(frame_data);

      if ($scope.editTypeValue === "instant") {
        $scope.editTypeValue = "null";
        $scope.radiansRotationValue = 0;
        $scope.hasEditScheduledValue = false;
        $scope.editHappenedValue = false;
      }

      requestAnimationFrame(updateOutputFile);
    }

    function setNormalizedTime() {
      $scope.normalizedTime = $scope.players[0].time();
      for (let i = 0; i < $scope.playerCount; i++) {
        if ($scope.players[i].time() > $scope.normalizedTime) {
          $scope.normalizedTime = $scope.players[i].time();
        }
      }
      if ($scope.contents.audio && $scope.contents.audio != "") {
        if ($scope.players[$scope.playerCount].time() > $scope.normalizedTime) {
          $scope.normalizedTime = $scope.players[$scope.playerCount].time();
        }
      }
      $scope.$apply();

      requestAnimationFrame(setNormalizedTime);
    }

    function computetotalThroughput() {
      const curTime = new Date().getTime(); // Get current time
      let TotalDataInAnInterval = 0; // Byte
      let TotalTimeInAnInterval = $scope.requestDuration; // ms
      let requestListLength = $scope.requestList.length;
      let requestListIndex = requestListLength - 1;
      let requestTimeIndex = curTime;
      while (requestListLength > 0 && requestListIndex >= 0) {
        let requestFinishTime =
          $scope.requestList[requestListIndex]._tfinish.getTime();
        let requestResponseTime =
          $scope.requestList[requestListIndex].tresponse.getTime();
        if (
          requestFinishTime > curTime - $scope.requestDuration &&
          requestResponseTime < curTime
        ) {
          // Accumulate the downloaded data (Byte)
          let requestDownloadBytes = $scope.requestList[
            requestListIndex
          ].trace.reduce((a, b) => a + b.b[0], 0);
          if (requestResponseTime > curTime - $scope.requestDuration) {
            if (requestFinishTime <= curTime) {
              TotalDataInAnInterval += requestDownloadBytes;
            } else {
              TotalDataInAnInterval +=
                requestDownloadBytes *
                ((curTime - requestResponseTime) /
                  (requestFinishTime - requestResponseTime));
            }
          } else {
            if (requestFinishTime <= curTime) {
              TotalDataInAnInterval +=
                requestDownloadBytes *
                ((requestFinishTime - (curTime - $scope.requestDuration)) /
                  (requestFinishTime - requestResponseTime));
            } else {
              TotalDataInAnInterval +=
                requestDownloadBytes *
                ($scope.requestDuration /
                  (requestFinishTime - requestResponseTime));
            }
          }
          // Subtract the free time (ms)
          if (requestTimeIndex > requestFinishTime) {
            TotalTimeInAnInterval -= requestTimeIndex - requestFinishTime;
          }
          // More the time index forward
          if (requestTimeIndex > requestResponseTime) {
            requestTimeIndex = requestResponseTime;
          }
        }
        requestListIndex--;
      }
      if (curTime - $scope.requestDuration < requestTimeIndex) {
        TotalTimeInAnInterval -=
          requestTimeIndex - (curTime - $scope.requestDuration);
      }
      // 这里强制将分母区间设置为3000
      TotalTimeInAnInterval = 3000;
      if (TotalDataInAnInterval != 0 && TotalTimeInAnInterval != 0) {
        $scope.totalThroughput = Math.round(
          (8 * TotalDataInAnInterval) / (TotalTimeInAnInterval / 1000)
        ); // bps
      }
    }
  },
]);
