<template>
  <v-system-bar
    height="32"
    app
    dense
    fixed
    style="-webkit-app-region: drag; padding-right: 0"
  >
    <img
      src="../build/icons/icon.png"
      style="margin: -8px 16px -8px 0px"
      width="22"
    />
    {{ appName }}
    <v-spacer></v-spacer>

    <v-btn
      @click.stop="winControl('minimize')"
      height="100%"
      class="no-drag"
      small
      tile
      depressed
      color="transparent"
    >
      <!-- <v-icon>mdi-window-minimize</v-icon> -->
      <!-- <v-icon>horizontal_rule</v-icon> -->
      <!-- <v-icon></v-icon> -->
      <v-icon>mdi-window-minimize</v-icon>
    </v-btn>

    <v-btn
      @click.stop="winControl('maximize')"
      height="100%"
      class="no-drag"
      small
      tile
      depressed
      color="transparent"
    >
      <!-- <v-icon v-if="isMaximized">mdi-window-restore</v-icon>
        <v-icon v-else>mdi-window-maximize</v-icon> -->
      <v-icon v-if="isMaximized">mdi-window-restore</v-icon>
      <v-icon v-else>mdi-window-maximize</v-icon>
    </v-btn>

    <v-dialog v-model="dialog" persistent max-width="290">
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          @click.stop="closeDialog = true"
          height="100%"
          class="no-drag close"
          small
          tile
          depressed
          color="transparent"
          v-bind="attrs"
          v-on="on"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
      <v-card>
        <v-card-title class="text-h5"> 现在关闭{{ appName }}? </v-card-title>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false"> 取消 </v-btn>
          <v-btn color="primary" text @click="winControl('close')">
            确定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-system-bar>
</template>

<script>
 
let browserWindow 
if(window.remote){
   browserWindow = window.remote.getCurrentWindow();
}

export default {
  data: () => ({
    appName: process.env.VUE_APP_PRODUCT_NAME,
    selectedItem: "",
    dialog: false,
    // 是最大化
    isMaximized: true,
  }),
  mounted() {
    browserWindow.on("unmaximize", () => {
      this.isMaximized = false;
    }),
      browserWindow.on("maximize", () => {
        this.isMaximized = true;
      });
  },
  methods: {
    winControl(action) {
      switch (action) {
        case "minimize":
          browserWindow.minimize();
          break;
        case "maximize":
          if (this.isMaximized) {
            browserWindow.unmaximize();
          } else {
            browserWindow.maximize();
          }
          this.isMaximized = !this.isMaximized;
          break;
        case "close":
          window.remote.app.exit(); 
          break;
        default:
          break;
      }
    },
  },
};
</script>
<style scoped>
/* .flat {
  border-radius: 0;
  box-shadow: none;
  padding: 0 14px !important;
  min-width: initial !important;
} */

.no-drag {
  -webkit-app-region: no-drag;
}
.close {
}
.close.v-btn:hover {
  color: rgb(232, 17, 35) !important;
}
.close.v-btn:hover .v-icon {
  color: #fff;
}
.close.v-btn:hover::before {
  opacity: 0.8;
}
</style>
