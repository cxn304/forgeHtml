const path = require('path');
const express = require('express');
var fs = require('fs'); //文件模块

const PORT = process.env.PORT || 5000;
const config = require('./config');
if (config.credentials.client_id == null || config.credentials.client_secret == null) {
    console.error('Missing FORGE_CLIENT_ID or FORGE_CLIENT_SECRET env. variables.');
    return;
}

let app = express();
app.use(express.static(path.join(__dirname, 'public')));    //public文件夹下面的网页,作为静态资源，直接加载
app.use(express.json({ limit: '50mb' }));
app.use('/api/forge/oauth', require('./routes/oauth'));
app.use('/api/forge/oss', require('./routes/oss'));
app.use('/api/forge/modelderivative', require('./routes/modelderivative'));
// 点云数据
app.get('/test_post/nn', function (req, res) {
    var file = './public/datas/idw.json'; //文件路径，相对路径
    fs.readFile(file, 'utf-8', function (err, data) {
        if (err) {
            console.log('failed file');
        }
        var upDate = data.toString();   //需让data转换为string
        res.send(upDate);
    });
});
// 施工数据管理上传数据
app.get('/constructTable', function (req, res) {
    var file = './public/datas/constructTable.json'; //文件路径，相对路径
    fs.readFile(file, 'utf-8', function (err, data) {
        if (err) {
            console.log('failed file');
        }
        var upDate = data.toString();   //需让data转换为string
        res.send(upDate);
    });
});
// 设计数据管理上传数据
app.get('/DesignTable', function (req, res) {
    var file = './public/datas/designTable.json'; //文件路径，相对路径
    fs.readFile(file, 'utf-8', function (err, data) {
        if (err) {
            console.log('failed file');
        }
        var upDate = data.toString();   //需让data转换为string
        res.send(upDate);
    });
});
// 接收创建文件夹请求
app.get('/quality-control/create-folder', function (req, res) {
    var response = { "data": "server get the data" };
    res.send(JSON.stringify(response));
    console.log(JSON.stringify(req.query)); //前台传回来的数据
    var file = path.join(__dirname, 'public/datas/test.json');  // 工艺库数据的文件
    fs.readFile(file, 'utf-8', function (err, data) {
        if (err) {
            res.send('网络存在问题');
        } else {
            var toDoJson = eval('(' + data + ')');  //不严格格式的json string都可以转为json对象
            toDoJson.push({ id: req.query.timestamp, parent: req.query.id, text: "试验新建文件夹", type: "folder" });
            fs.writeFileSync('public/datas/test.json', JSON.stringify(toDoJson), function (err) { });
        }
    })
})
// 接收删除文件夹请求
app.get('/quality-control/delete-node', function (req, res) {
    function nodes(idname, itoDoJson){  //idname表示此节点id，递归删除所有子文件夹及本身
        for (var i = 0; i < itoDoJson.length; i++) {
            if (itoDoJson[i].id == idname) {   //这个是文件夹本身
                itoDoJson.splice(i, 1);
            }
            // 此时toDoJson[i]的parent是已删除的那个文件夹，说明toDoJson[i]是其子文件夹，
            // 那么他有可能是某个节点的父节点，所以把其id也递归下去
            if(itoDoJson[i].parent == idname){  
                var loopname=itoDoJson[i].id;
                itoDoJson.splice(i, 1);
                i--;    // i--的目的在于：splice会改变数组长度，删除项目后，得从上一个i开始判断一次，不然会漏掉补位的
                nodes(loopname, itoDoJson);
            }
        }
    }

    console.log(JSON.stringify(req.query)); //前台传回来的数据
    var file = path.join(__dirname, 'public/datas/test.json');  // 工艺库数据的文件
    fs.readFile(file, 'utf-8', function (err, data) {
        if (err) {
            res.send('网络存在问题');
        } else {
            var toDoJson = eval('(' + data + ')');  //不严格格式的json string都可以转为json对象
            var idname=req.query.id;
            nodes(idname, toDoJson);
            fs.writeFileSync('public/datas/test.json', JSON.stringify(toDoJson), function (err) { });
            res.send(toDoJson);
        }
    })
})

//如果404，则重定向
app.get('*', function (req, res) {
    res.sendfile('./public/forgeTable.html');
});
app.use((err, req, res, next) => {
    console.error(err);
    res.status(err.statusCode).json(err);
});

app.listen(PORT, () => { console.log(`Server listening on port ${PORT}`); });