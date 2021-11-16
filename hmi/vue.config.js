/*
 * @Description  : 
 * @Author       : zyl
 * @Date         : 2021-10-27 16:49:59
 * @LastEditTime : 2021-11-08 10:22:35
 * @FilePath     : \\splicetools\\hmi\\vue.config.js
 */
 
module.exports = {
  pluginOptions: {
    electronBuilder: {
      preload: 'src/preload.js',
      builderOptions: {    
        copyright:"ZYL",
        productName: process.env.VUE_APP_PRODUCT_NAME, 
        publish:  null, 
        extraFiles: [
          {
            "from": "../backend",
            "to": "./backend"  
          },
          {
            "from": "../config.json",
            "to": "./config.json"  
          },
          {
            "from": "../Python38",
            "to": "./Python38"  
          }
        ]

        }
 
    }
  },
  configureWebpack:{
    
    //target:'electron-renderer',
    // externals: [
    //   //...Object.keys(dependencies || {}).filter(d => !whiteListedModules.includes(d))
    // ],
  },

  transpileDependencies: [
    'vuetify'
  ]
}
