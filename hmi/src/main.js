/*
 * @Description  : 
 * @Author       : zyl
 * @Date         : 2021-10-27 16:42:07
 * @LastEditTime : 2021-11-08 10:22:05
 * @FilePath     : \\splicetools\\hmi\\src\\main.js
 */
import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import '@mdi/font/css/materialdesignicons.css'
 
 
new Vue({
 vuetify,
 render: h => h(App)
}).$mount('#app');
 