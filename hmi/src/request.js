/*
 * @Description  : 
 * @Author       : zyl
 * @Date         : 2021-11-04 11:16:49
 * @LastEditTime : 2021-11-08 10:22:16
 * @FilePath     : \\splicetools\\hmi\\src\\request.js
 */
import axios from "axios"
axios.defaults.timeout = 0;
axios.defaults.baseURL = `http://localhost:${process.env.VUE_APP_SERVER_PORT}`;
axios.interceptors.response.use(
  (res) => {
    return res.data ? res.data : res;
  },
  (err) => {
    if (err.response) {
      switch (err.response.status) {
        case 400:
          alert("接口不存在");
          break;
        case 500:
          if (err.response.data.error) {
            alert(err.response.data.error);
          }
          break;
      }
    }
    return Promise.resolve(err);
  }
);
export default  axios