/*
 * @Description  : 
 * @Author       : zyl
 * @Date         : 2021-10-28 10:51:52
 * @LastEditTime : 2021-11-08 11:22:29
 * @FilePath     : \\splicetools\\hmi\\src\\server.js
 */


const sqlite3 = require('sqlite3').verbose();
const express = require('express');
const http = require('http');
const PythonShell = require('python-shell').PythonShell;
const path = require('path');
const fs = require('fs-extra');

const app = express();
const router = express.Router();
const server = http.createServer(app);
// const dotenv = require("dotenv")
// dotenv.config()
const port = process.env.VUE_APP_SERVER_PORT
const isDevelopment = process.env.NODE_ENV !== 'production'

//设置跨域访问
app.all('*', function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");
  res.header("Access-Control-Allow-Methods", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type");
  // res.header("Content-Type", "application/json;charset=utf-8");
  next();
});

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
const dbFolder = isDevelopment? 'backend_original':'backend'
var db = new sqlite3.Database(path.join(__dirname, `..\\..\\${dbFolder}\\app.db`));

const mixProcessToCallbackWhenSuccess = (res, processWhenSuccess) => {
  return (err, result) => { 
    if (err) {
      res.status(500).json({ "error": err.message });
      return;
    }
    try {
      let jsonString = Array.isArray(result) ? result[result.length - 1] : result
      const json = JSON.parse(jsonString)

      if (json.code == 200) {
        processWhenSuccess(res, json.data)
      } else {
        res.status(500).json(json);
      }

    } catch {
      res.json({ "error": "服务端返回结果异常" })
    }
  }
}

function pythonProcss(scriptName, args, callback) {
  const options = {}
  const pythonPath = path.join(__dirname, "..\\..\\Python38\\python.exe")
  options.pythonPath = pythonPath
  options.args = args
  let pyPathBase = isDevelopment? `..\\..\\backend_original\\${scriptName}.py`:`..\\..\\backend\\${scriptName}.pyc`
  const pyPath = path.join(__dirname, pyPathBase)
  PythonShell.run(pyPath, options, callback)
}



const uploadVideo = async (req, res) => {
  try {
    let storage = multer.diskStorage({
      destination: (req, file, cb) => {
        cb(null, __basedir + "/resources/static/assets/uploads/");
      },
      filename: (req, file, cb) => {
        cb(null, file.originalname);
      },
    });

    let uploadFile = multer({
      storage: storage,
      limits: { fileSize: maxSize },
    }).single("file");

    await uploadFile(req, res);

    if (req.file == undefined) {
      return res.status(400).send({ message: "Please upload a file!" });
    }

    res.status(200).send({
      message: "Uploaded the file successfully: " + req.file.originalname,
    });
  } catch (err) {
    res.status(500).send({
      message: `Could not upload the file: ${req.file.originalname}. ${err}`,
    });
  }
};

const getVideoInfo = (req, res) => {
  var errors = []
  if (!req.query.videoPath) {
    errors.push("No videoPath specified");
  }
  //reserved for other errors...
  if (errors.length) {
    res.status(400).json({ "error": errors.join(",") });
    return;
  }
  const videoPath = decodeURI(req.query.videoPath)
  const scriptName = 'info'
  const args = [videoPath]

  processWhenSuccess = (res, data) => fs.stat(videoPath, (err, stats) => {
    if (err) {
      res.status(500).json({ "error": err.message });
      return;
    }
    res.json({ ...data, ...stats })
  })
  callback = mixProcessToCallbackWhenSuccess(res, processWhenSuccess)
  pythonProcss(scriptName, args, callback)
}

const postProject = (req, res) => {
  var errors = []
  if (!req.query.videoPath) {
    errors.push("No videoPath specified");
  }
  //reserved for other errors...
  if (errors.length) {
    res.status(400).json({ "error": errors.join(",") });
    return;
  }
  const videoPath = decodeURI(req.query.videoPath)
  const scriptName = 'main'
  const args = [videoPath, req.params.projectId]
  processWhenSuccess = (res, data) => {
    if (data.success) {  
      const image =data.imgPath
      if(image){
        fs.readFile(image, (err, data) => {
          if (err) {
            res.status(500).json({ "error": err.message });
            return;
          }
          res.send(data)
        })
      }else{
        res.json({success:true,image:null})
      }

    }
  }
  const callback = mixProcessToCallbackWhenSuccess(res, processWhenSuccess)
  pythonProcss(scriptName, args, callback)
}

const getProjectProgress = (req, res) => {
  const sql = "select * from log where projectId = ? order by id desc limit 1"
  const params = [req.params.projectId]
  db.get(sql, params, function (err, row) {
    if (err) {
      res.status(500).json({ "error": err.message });
      return;
    }
    res.json(row)
  });
}

const getDefaultConfig = (req, res) => {
  let jsonPathBase = `..\\..\\config.json`
  const jsonPath = path.join(__dirname, jsonPathBase)
  fs.readFile(jsonPath, 'utf8', function (err, data) {
    if (err) {
      res.status(500).json({ "error": err.message });
      return;
    }
    try {
      res.json(JSON.parse(data))
    } catch {
      res.status(500).json({ "error": "不是一个有效的JSON文件" });
    }
  })

}

const updateConfig = (req, res) => {
  const data = {
    centx: req.body.centx,
    centy: req.body.centy,
    picWidth: req.body.picWidth,
    radiusMax: req.body.radiusMax,
    start: req.body.start,
    interval: req.body.interval,
    processPath: req.body.processPath
  }
  var sql = `UPDATE config set 
  centx = COALESCE(?,centx), 
  centy = COALESCE(?,centy), 
  picWidth = COALESCE(?,picWidth),
  radiusMax = COALESCE(?,radiusMax), 
  start = COALESCE(?,start), 
  interval = COALESCE(?,interval),
  processPath = COALESCE(?,processPath) 
  WHERE id = ?`
  var params = [data.centx, data.centy, data.picWidth, data.radiusMax, data.start, data.interval, data.processPath, req.params.id]
  db.run(sql, params, function (err, result) {
    if (err) {
      res.status(500).json({ "error": err.message })
      return;
    }
    res.json({
      changes: this.changes
    })
  });
}

const getLastConfig = (req, res) => {
  const sql = 'select * from config limit 1'
  db.get(sql, function (err, row) {
    if (err) {
      res.status(500).json({ "error": err.message });
      return;
    }
    res.json(row)
  });
}

 


let initRoutes = (app) => {
  router.post("/api/video/upload", uploadVideo)
  router.get("/api/video/info", getVideoInfo)
  router.post("/api/video/process/:projectId", postProject)
  router.get("/api/log/:projectId", getProjectProgress)
  router.get("/api/config/default", getDefaultConfig)
  router.put("/api/config/:id", updateConfig)
  router.get("/api/config/", getLastConfig)

  app.use(router);
};

initRoutes(app);
server.listen(port, function () { console.log(`Server listening on port: ${port}`) });
module.exports = app;
