/*
 * @Description  : 
 * @Author       : zyl
 * @Date         : 2021-10-28 12:01:29
 * @LastEditTime : 2021-11-08 10:21:47
 * @FilePath     : \\splicetools\\hmi\\src\\plugins\\vuetify.js
 */

import Vue from 'vue';
/* disable-next-line */
import Vuetify , {
    VSnackbar,
    VIcon
  } from 'vuetify/lib';

Vue.use(Vuetify,{
    components: {
        VSnackbar,
        VIcon 
      }
});

export default new Vuetify({
});
