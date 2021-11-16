<template>
  <v-app>
    <system-bar />
    <v-snackbar
      :top="true"
      :timeout="timeout"
      v-model="snackbar"
      :color="snackbarColor"
    >
      {{ message }}

      <template v-slot:action="{ attrs }">
        <v-btn color="#fff" text v-bind="attrs" @click="snackbar = false">
          关闭
        </v-btn>
      </template>
    </v-snackbar>

    <v-app-bar app color="#fff" white>
      <v-file-input
        :disabled="isInProcess"
        prepend-icon="mdi-video"
        filled
        full-width
        label="视频"
        @change="change"
        accept="video/*"
        hide-details
        outlined
        dense
        suffix="导入视频"
        :clearable="false"
      >
        <template v-slot:selection="{ text }">
          <v-chip small label color="primary">
            {{ videoPath ? videoPath : text }}
          </v-chip>
        </template>
      </v-file-input>

      <v-spacer></v-spacer>

      <v-dialog v-model="dialog" persistent max-width="600px">
        <template v-slot:activator="{ on, attrs }">
          <v-btn color="green" dark v-bind="attrs" v-on="on" class="mr-5">
            <v-icon class="mr-1" right dark> mdi-tune </v-icon>
            参数设置
          </v-btn>
        </template>
        <v-card>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    label="图像开始位置 *"
                    required
                    :disabled="isInProcess"
                    v-model="start"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    label="图像间隔 *"
                    required
                    :disabled="isInProcess"
                    v-model="interval"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    label="图像中心x像素 *"
                    required
                    :disabled="isInProcess"
                    v-model="centy"
                  ></v-text-field>
                </v-col>

                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    label="图像中心y像素 *"
                    v-model="centx"
                    :disabled="isInProcess"
                    required
                  ></v-text-field>
                </v-col>

                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    label="圆环宽度 *"
                    v-model="picWidth"
                    :disabled="isInProcess"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    label="圆环半径限制 *"
                    v-model="radiusMax"
                    :disabled="isInProcess"
                    required
                  ></v-text-field>
                </v-col>

                <v-col cols="12" sm="12" md="12">
                  <v-text-field
                    hide-details
                    suffix="工作目录"
                    dense
                    :label="
                      isElectron
                        ? '请选择工作目录 *'
                        : '在浏览器中无法选择目录,请手动输入目录 *'
                    "
                    :disabled="isInProcess"
                    :readonly="isElectron"
                    @click="changeDirectory"
                    placeholder="工作目录"
                    v-model="processPath"
                    outlined
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
            <small>* 为必填项</small>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="getDefault" :disabled="isInProcess">
              恢复默认值
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="dialog = false">
              取消
            </v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="saveConfig"
              :disabled="isInProcess"
            >
              保存
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-btn
        target="_blank"
        color="primary"
        @click="beginAnalysis"
        :loading="isInProcess"
      >
        <span class="mr-2">开始分析</span>
      </v-btn>
    </v-app-bar>

    <v-main :style="{ height: height }">
      <div class="d-flex">
        <div style="width: 400px">
          <v-card flat width="400">
            <v-list class="transparent">
              <v-list-item>
                <v-list-item-title> 文件大小</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ Math.floor(videoProps.size / 1024 / 1024) }}M
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title>创建日期</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ videoProps.mtime }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title> 时长</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ Math.floor(videoProps.duration) }}秒
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title> 帧数</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ videoProps.num_frames }}帧
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card>

          <div>
            <v-stepper flat>
              <v-stepper-header>
                <v-stepper-step
                  step="1"
                  :complete="stage > 1 || isSuccessFinished"
                >
                  获取帧
                </v-stepper-step>

                <v-divider></v-divider>

                <v-stepper-step
                  step="2"
                  :complete="stage > 2 || isSuccessFinished"
                >
                  展开图像
                </v-stepper-step>

                <v-divider></v-divider>

                <v-stepper-step step="3" :complete="isSuccessFinished">
                  合并图像
                </v-stepper-step>

                <v-divider></v-divider>
              </v-stepper-header>
            </v-stepper>
            <v-progress-linear
              v-model="progress"
              height="25"
              v-show="!isSuccessFinished || isInProcess"
            >
              <strong
                >当前第 {{ current }} 张/共 {{ total }} 张
                {{
                  stage == 2 ? `本阶段预计还需${float2hhmm(timePredict)}` : ""
                }}</strong
              >
            </v-progress-linear>
          </div>
        </div>

        <div style="width: calc(100vw - 400px)">
          <div v-show="isSuccessFinished" class="ma-5">
            <div
              class="images"
              v-viewer
              :style="{ height: picHeight }"
              style="overflow: auto"
            >
              <img
                v-for="src in images"
                :key="src"
                :src="src"
                style="width: 100%"
              />
            </div>

            <v-btn
              type="button"
              color="primary"
              class="ma-5 ml-0"
              @click="saveImage"
            >
              下载图片</v-btn
            >
          </div>
          <div v-if="isInProcess" :style="{ height: height }" class="ma-5">
            视频处理中....,处理完成后的图片将在此处显示
          </div>
        </div>
      </div>
    </v-main>
  </v-app>
</template>

<script>
import moment from "moment";
import axios from "./request";
import SystemBar from "./SystemBar.vue";
import "viewerjs/dist/viewer.css";
import VueViewer from "v-viewer";
import Vue from "vue";
import shortid from "shortid";
Vue.use(VueViewer);

const isElectron = navigator.userAgent.toLowerCase().indexOf(" electron/") > -1;
export default {
  name: "App",
  components: { SystemBar },
  data: () => ({
    isElectron,
    rules: [
      (value) => !!value || "此项为必填.",
      (value) => {
        const pattern = /^(0\.\d+|1)$/g;
        return pattern.test(value) || "只能为正整数";
      },
    ],
    centx: "",
    centy: "",
    start: "",
    interval: "",
    picWidth: "",
    radiusMax: "",
    processPath: "",
    id: null,
    dialog: false,
    intervalTimer: null,
    value: null,
    videoPath: "",
    timeout: 5000,
    message: "",
    snackbarColor: "",
    disabled: true,
    isInProcess: false,
    images: [],
    snackbar: false,
    current: 0,
    total: 0,
    fileObj: null,
    stage: 0,
    isSuccessFinished: false,
    timePredict: 0,
    videoProps: {
      size: 0,
      mtime: "",
      duration: "",
      num_frames: "",
    },
  }),
  computed: {
    progress() {
      const progress =
        this.total == 0 ? 100 : (this.current * 100) / this.total;

      return progress;
    },
    picHeight() {
      return `calc(100vh - ${
        this.$vuetify.application.top + this.$vuetify.application.bar + 100
      }px)`;
    },
    height() {
      return `calc(100vh - ${
        this.$vuetify.application.top + this.$vuetify.application.bar
      }px)`;
    },
  },
  filters: {},
  watch: {
    workDir(v) {
      console.log(v);
    },
    dialog: {
      handler(v) {
        if (v) {
          axios.get(`/api/config`).then((data) => {
            for (let x in data) {
              this[x] = data[x];
            }
          });
        }
      },
    },
    isInProcess: {
      handler(v) {
        if (!v) {
          window.clearInterval(this.intervalTimer);
        }
      },
    },
  },
  created() {},
  mounted() {
    // if (this.isBrowser && window.sessionStorage.projectId > 1) {
    //   this.getLog();
    // }
  },
  methods: {
    float2hhmm(float) {
      if (float * 60 > 0 && float * 60 < 1) {
        return 1 + "分钟";
      }
      return float > 1
        ? `${Math.floor(float)}小时${Math.floor(
            (float - Math.floor(float)) * 60
          )}分钟`
        : Math.floor(float * 60) + "分钟";
    },
    saveConfig() {
      const data = {
        centx: this.centx,
        centy: this.centy,
        picWidth: this.picWidth,
        radiusMax: this.radiusMax,
        start: this.start,
        interval: this.interval,
        processPath: this.processPath,
      };
      if (!this.id) {
        this.warning("参数还未加载");
        return false;
      }
      axios.put(`/api/config/${this.id}`, data).then((data) => {
        if (data.changes && data.changes == 1) {
          this.success("保存成功", 1000);
          this.dialog = false;
        } else {
          console.log(data);
        }
      });
    },
    getDefault() {
      axios("/api/config/default").then((data) => {
        for (let x in data) {
          this[x] = data[x];
        }
      });
    },

    showImage(blob) {
      this.images = [];
      window.sessionStorage.projectId = 0;
      const url = window.URL.createObjectURL(blob);
      this.images.push(url);
    },
    getLog() {
      this.intervalTimer = setInterval(() => {
        axios
          .get(`/api/log/${window.sessionStorage.projectId}`)
          .then((data) => {
            this.current = data.current;
            this.timeElapsed = data.timeElapsed;
            this.total = data.total;
            this.stage = data.stage;
            if (data.stage == 2) {
              this.timePredict =
                Math.round(
                  (((this.total - this.current) * this.timeElapsed) / 3600) *
                    100,
                  2
                ) / 100;
            }
          });
      }, 5000);
    },
    getBlob(url, cb) {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.responseType = "blob";
      xhr.onload = function () {
        if (xhr.status === 200) {
          cb(xhr.response);
        }
      };
      xhr.send();
    },
    saveAs(blob, filename) {
      var link = document.createElement("a");
      var body = document.querySelector("body");
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      // fix Firefox
      link.style.display = "none";
      body.appendChild(link);
      link.click();
      body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    },
    saveImage() {
      const fileName = this.videoPath.replace(/(.*\\)*([^.]+).*/gi, "$2");
      this.getBlob(this.images[0], (blob) => {
        this.saveAs(blob, fileName + ".jpg");
      });
    },
    setSnackbar(message, color, timeout) {
      this.message = message;
      this.snackbar = true;
      this.timeout = timeout;
      this.snackbarColor = color;
    },
    error(message, timeout = 5000) {
      this.setSnackbar(message, "error", timeout);
    },
    warning(message, timeout = 5000) {
      this.setSnackbar(message, "warning", timeout);
    },
    success(message, timeout = 5000) {
      this.setSnackbar(message, "success", timeout);
    },
    show2() {
      this.$viewerApi({
        options: {
          fullscreen: false,
          loading: true,
          loop: false,
          inline: true,
          button: true,
          navbar: true,
          title: true,
          toolbar: true,
          tooltip: true,
          movable: true,
          zoomable: true,
          rotatable: true,
          scalable: true,
          transition: true,
          keyboard: true,
        },
        images: this.images,
      });
    },
    stopAnalysis() {
      this.isInProcess = false;
      this.disabled = false;
    },
    beginAnalysis() {
      this.stage = 1
      this.current = 0
      this.total =  0
      // const pathDir = (pathStr) => {
      //   return pathStr
      //     .split("\\")
      //     .slice(0, pathStr.split("\\").length - 1)
      //     .join("\\");
      // };
      // const isChinese = (str) => {
      //   return escape(pathDir(str)).indexOf("%u") > 0;
      // };
      if (isElectron) {
        if (!this.videoPath) {
          this.error("请选择一个视频");
          return false;
        }
        // if (this.videoPath) {
        //   if (isChinese(this.videoPath)) {
        //     this.error("路径中不能包含中文");
        //     return false;
        //   }
        // }
      } else {
        let formData = new FormData();
        formData.append("file", this.fileObj);
        return axios.post("/api/video/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          onUploadProgress: (event) => {
            console.log(event);
          },
        });
      }

      axios.get(`/api/video/info?videoPath=${this.videoPath}`).then((data) => {
        data.mtime = moment(data.mtime).format("YYYY-MM-DD HH:mm");
        this.videoProps.mtime = data.mtime;
        this.videoProps.size = data.size;
        this.videoProps.duration = data.duration;
        this.videoProps.num_frames = data.num_frames;
      });
      this.projectId = shortid.generate();
      window.sessionStorage.projectId = this.projectId;
      this.isInProcess = true;
      this.isSuccessFinished = false;
      this.images = [];
      axios
        .post(
          `/api/video/process/${this.projectId}?videoPath=${this.videoPath}`,
          {},
          {
            responseType: "blob",
          }
        )
        .then((blob) => {
          this.isInProcess = false;
          this.isSuccessFinished = true;
          blob.text().then((string) => {
            try {
              const json = JSON.parse(string);
              if (json.success) {
                console.log(json.image);
              }
            } catch {
              this.showImage(blob);
            }
          });
        })
        .catch((err) => {
          console.log(5678);
          console.log(err);
          this.isInProcess = false;
        });
      this.getLog();
    },
    change(fileObj) {
      this.fileObj = fileObj;
      if (typeof fileObj != "undefined") {
        this.videoPath = fileObj.path;
      } else {
        this.videoPath = "";
      }
    },
    changesData() {
      console.log(this.$refs.file.files);
      // 获取filelist
    },
    // 上传
    //  uploadFile () {
    //       let formData = new window.FormData()
    //       for (let i = 0; i < this.fileList.length; i++) {  // 每个file append到formdata里
    //         formData.append('file', this.fileList[i])
    //       }
    //       let url = Vue.prototype.API_URL + '/imageCompare'
    //       axios({
    //         method: 'post',
    //         url: url,
    //         data: formData,
    //         headers: {'Content-Type': 'multipart/form-data'}
    //       }).then(function (res) {
    //       })
    //     },

    changeDirectory() {
      if (window.remote) {
        let browserWindow = window.remote.getCurrentWindow();
        const options = {
          title: "请选择工作目录",
          // defaultPath,
          buttonLabel: "确定",
          properties: ["openDirectory", "createDirectory"],
        };
        const dialog = window.remote.dialog;
        const message = dialog.showOpenDialogSync(browserWindow, options);

        if (message) {
          const filePath = message[0];
          this.processPath = filePath;
        }
      }
    },
  },
};
</script>

<style  >
html {
  overflow: hidden;
}
::selection {
  background: #d3d3d3;
}
.rotated {
  transform: rotate(90deg); /* Equal to rotateZ(45deg) */
}
</style>