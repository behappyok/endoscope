/*
 * @Description  : 
 * @Author       : zyl
 * @Date         : 2021-10-27 16:45:33
 * @LastEditTime : 2021-11-08 10:21:59
 * @FilePath     : \\splicetools\\hmi\\src\\background.js
 */
'use strict'

import { app, protocol, BrowserWindow,globalShortcut } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS3_DEVTOOLS } from 'electron-devtools-installer'
import querystring from "querystring";
import path from 'path'
const isDevelopment = process.env.NODE_ENV !== 'production'
const server = require('./server')
 

// Scheme must be registered before the app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])


async function createWindow() {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    frame: false, 
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      devTools: isDevelopment,
      experimentalFeatures: true,
      webSecurity: false,
      enableRemoteModule: true,
      // Use pluginOptions.nodeIntegration, leave this alone
      // See nklayman.github.io/vue-cli-plugin-electron-builder/guide/security.html#node-integration for more info
      nodeIntegration: process.env.ELECTRON_NODE_INTEGRATION,
      contextIsolation: false //!process.env.ELECTRON_NODE_INTEGRATION
      
    }
  })

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    await win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    createProtocol('app')
    // Load the index.html when not in development
    win.loadURL('app://./index.html')
  }
  return win
}

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.

function slash(path) {
  return path.replaceAll('\\', '/')
}
app.on('ready', async () => {

  
  if (isDevelopment && !process.env.IS_TEST) {
    // Install Vue Devtools
    try {
      await installExtension(VUEJS3_DEVTOOLS)
    } catch (e) {
      console.error('Vue Devtools failed to install:', e.toString())
    }
    // globalShortcut.register('Shift+CommandOrControl+I', () => {
    //   mainWindow.webContents.toggleDevTools();
    // });
  } else {
    globalShortcut.register('CommandOrControl+R', () => {
      console.log("CommandOrControl+R is pressed: Shortcut Disabled");
    });
    globalShortcut.register('Shift+CommandOrControl+R', () => {
      console.log("Shift+CommandOrControl+R is pressed: Shortcut Disabled");
    });
  }
   const mainWindow = await createWindow()
 
  //  api.get("/api/close", (req, res) => {
  //   mainWindow.minimize()
  //   mainWindow.close()
      
 
  //   })

    //注册FileProtocol
    protocol.registerFileProtocol('file', (request, callback) => {
      //截取file:///之后的内容，也就是我们需要的
      const url = slash(querystring.unescape(request.url.substr(8)))
      //使用callback获取真正指向内容
      callback({ path: url })
    })
})

// Exit cleanly on request from parent process in development mode.
if (isDevelopment) {
  if (process.platform === 'win32') {
    process.on('message', (data) => {
      if (data === 'graceful-exit') {
        app.quit()
      }
    })
  } else {
    process.on('SIGTERM', () => {
      app.quit()
    })
  }
}
