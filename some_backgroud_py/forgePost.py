# -*- coding:utf-8 -*-
"""
by:cxn
"""

import requests, os, re, json, base64, time, datetime
import pymysql
import pandas as pd
import numpy as np


class getToken:
    def __init__(self, bucketName, file_upload):
        self.bucketName = bucketName
        self.file_upload = file_upload

    # 第一步用账号密码连接,获取token
    @staticmethod
    def get_token():
        url = 'https://developer.api.autodesk.com/authentication/v1/authenticate'
        mData = {'client_id': 'Qeul9eD5jp0ySqJrdDnvjEkqmrryZqPO',
                 'client_secret': 'KOB1WypAjo6XO3mw', 'grant_type': 'client_credentials'
            , 'scope': 'data:read viewables:read bucket:read bucket:create data:write'}
        header0 = {'Content-Type': 'application/x-www-form-urlencoded'}
        response0 = requests.post(url, headers=header0, data=mData)
        return response0

    # 传入bucketName
    def post_bucket_name(self, token_number):
        tempToken = re.findall('"(.*?)"', token_number)  # response0.text
        url1 = 'https://developer.api.autodesk.com/oss/v2/buckets'
        autho = tempToken[3] + ' ' + tempToken[1]  # 有Bearer的token
        header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
        mData1 = {'bucketKey': self.bucketName, 'policyKey': 'transient'}
        requests.post(url1, headers=header, data=json.dumps(mData1))
        return autho, mData1, tempToken  # 传出autho

    # 检查是否在云端建立了bucketName
    def _check_bucket_name(self, autho, mData1):
        header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
        url2 = 'https://developer.api.autodesk.com/oss/v2/buckets/' + self.bucketName + '/details'  # 与第二步的headers和data一样
        responsed2 = requests.get(url2, headers=header, data=json.dumps(mData1))
        return responsed2

    # 传文件
    def upload_file(self, autho):
        header3 = {'Authorization': autho, 'Content-Type': 'application/octet-stream',
                   'Content-Length': str(os.path.getsize(self.file_upload))}
        url3 = 'https://developer.api.autodesk.com/oss/v2/buckets/' + self.bucketName + '/objects/' + self.file_upload
        with open(self.file_upload, mode='rb') as fo:
            sn = fo.read(os.path.getsize(self.file_upload))
            fw = open(self.file_upload, "wb")
            fw.write(sn)  # fw的这些操作就是因为读filename3时文件大小会出现问题，重新写一次二进制
            fw.close()
            fw = open(self.file_upload, "rb")
            response3 = requests.put(url3, headers=header3, data=fw)
            fw.close()
            return response3

    # 用于解urn码,并发起转换
    def do_urn(self, autho, urn_number):
        header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
        tempUrn = re.findall('"(.*?)"', urn_number)  # 用于解码,传文件的response3.text
        urnEncode = base64.b64encode(tempUrn[3].encode('utf-8'))
        urnEncodeEnd = str(urnEncode, 'utf-8').replace("=", "")
        mData4 = {"input": {"urn": urnEncodeEnd}, "output": {"formats": [{"type": "svf", "views": ["2d", "3d"]}]}}
        url4 = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/job'
        response4 = requests.post(url4, headers=header, data=json.dumps(mData4))
        return response4, urnEncodeEnd

    # 检查模型是否传完,如果报401，则是token问题
    def _check_model_uploaded(self, autho, urnEncodeEnd):
        header5 = {'Authorization': autho}
        url5 = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/' + urnEncodeEnd + '/manifest'
        response5 = requests.get(url5, headers=header5)
        return response5

    # 检查是否有文件
    def check_file_uploaded(self, autho):
        header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
        urnDecode = 'urn:adsk.objects:os.object:' + self.bucketName + '/' + self.file_upload
        urnEncode = base64.b64encode(urnDecode.encode('utf-8'))
        urnEncodeEnd = str(urnEncode, 'utf-8').replace("=", "")
        mData4 = {"input": {"urn": urnEncodeEnd}, "output": {"formats": [{"type": "svf", "views": ["2d", "3d"]}]}}
        url4 = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/job'
        response = requests.post(url4, headers=header, data=json.dumps(mData4))
        return response, response.status_code, urnEncodeEnd

    # 对原有html网页文件进行修改(弃用)
    def _change_html_file(self, tempToken, urnEncodeEnd):
        dir_road = "./"
        for root, dirs, files in os.walk(dir_road):
            for file in files:
                if file == 'hahahaha':
                    with open(os.path.join(root, file), encoding='utf-8', mode='r+') as Html_file:
                        htmlHandle = Html_file.read()
                        assesTokenPatten = re.compile(r'var accessToken =.*')
                        assesTokenReplace = "var accessToken = '" + tempToken[1] + "';"  # tempToken[1]是字符串，token
                        htmlHandle = re.sub(assesTokenPatten, assesTokenReplace, htmlHandle)
                        assesDocumentIdPatten = re.compile(r'var documentId =.*')
                        assesDocumentIdReplace = "var documentId = 'urn:" + urnEncodeEnd + "';"  # urnEncodeEnd是最终值
                        assesDocumentIdOut = re.sub(assesDocumentIdPatten, assesDocumentIdReplace,
                                                    htmlHandle)  # 最终替换完成的str

                    with open(os.path.join(root, file), encoding='utf-8', mode='w+') as newHtml:
                        newHtml.write(assesDocumentIdOut)

    def _main_code(self):  # 改变文件的方法(弃用)
        response_zero = self.get_token()
        au_tho, m_data, temp_token = self.post_bucket_name(response_zero.text)
        # response_two = _check_bucket_name(au_tho, m_data)
        fileResponse, html_states, urn_encode = self.check_file_uploaded(au_tho)
        if html_states == 201:
            self._change_html_file(temp_token, urn_encode)
        else:
            print(self.file_upload + ' is uploading... ' + str(datetime.datetime.now()))
            response_three = self.upload_file(au_tho)
            response_four, urn_encode = self.do_urn(au_tho, response_three.text)
            # response_five = _check_model_uploaded(au_tho, urn_encode)
            self._change_html_file(temp_token, urn_encode)
            time.sleep(2)
            print(self.file_upload + ' is uploaded ' + str(datetime.datetime.now()))
        print('hahahaha' + ' is loaded ' + str(datetime.datetime.now()))

    def getTokenUrn(self):  # 直接传token和urn的方法，顺带传文件
        response_zero = self.get_token()
        au_tho, m_data, temp_token = self.post_bucket_name(response_zero.text)
        fileResponse, html_states, urn_encode = self.check_file_uploaded(au_tho)
        if html_states == 201:
            return temp_token[1], urn_encode
        else:
            print(self.file_upload + ' is uploading... ' + str(datetime.datetime.now()))
            response_three = self.upload_file(au_tho)
            response_four, urn_encode = self.do_urn(au_tho, response_three.text)
            self._change_html_file(temp_token, urn_encode)
            time.sleep(2)
            print(self.file_upload + ' is uploaded ' + str(datetime.datetime.now()))
            return temp_token[1], urn_encode  # 纯粹的urn_encode


# 返回json格式的mysql数据库文件,日期需转换时间戳
def forgeTableData(ipString):
    connected = pymysql.connect(host=ipString, port=3306, user='cxn', password='123456', db='unitymonitor',
                                charset='utf8mb4')
    # 使用cursor()方法获取操作游标
    cur = connected.cursor()
    # 1.查询操作  # 编写sql 查询语句  user 对应我的表名
    nrsql = "select * from forgetest"  # 内容
    btsql = "show columns from forgetest"  # 表头
    try:
        cur.execute(nrsql)  # 执行sql语句
        results = cur.fetchall()  # 返回结果为tuple,可直接转为dataframe
        forge_db = pd.DataFrame(list(results))
        cur.execute(btsql)
        results = cur.fetchall()
        fbt = pd.DataFrame(list(results))
        bt = fbt.iloc[:, 0]
        forge_db.columns = bt
        forge_json = forge_db.to_json(orient='records', force_ascii=False)
        timePatten = re.compile(r'(?<="ModifiedBy":)[0-9]+(?=,)')
        timePattenFind = re.findall(timePatten, forge_json)
        for times in timePattenFind:
            timeInt = times[:-3]
            timeInt = int(timeInt)
            dateArray = datetime.datetime.utcfromtimestamp(timeInt)  # 时间戳转换为指定格式
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            otherStyleTime = '"' + str(otherStyleTime) + '"'
            timeSubPatten = re.compile(times)
            forge_json = re.sub(timeSubPatten, otherStyleTime, forge_json)
    except Exception as e:
        raise e
    finally:
        connected.close()  # 关闭连接
    return forge_json


# 覆写forgedb.js文件以改变其json数据
def changeForgedb(fJson):
    jsonPatten = re.compile(r'forgedb\.clients = .*];', re.S)
    jsonReplace = "forgedb.clients = " + fJson + ";"
    filePath = "F:/GraphtestUnity/moban3793/assets/js/lib/jsgrid/forgedb.js"
    with open(filePath, mode='r+', encoding='UTF-8') as f:
        files = f.read()
        files = re.sub(jsonPatten, jsonReplace, files)
    with open(filePath, mode='w+', encoding='UTF-8') as newFile:
        newFile.write(files)


# 返回经反距离插值法的值
def myIDW(a, b, pi, yjz):
    reArray = yjz.reshape(-1)
    k = np.alen(pi[1])  # 矩阵长度
    ptn = []
    for ii in range(k):
        dis = np.sqrt((a - pi[0][ii]) * (a - pi[0][ii]) + (b - pi[1][ii]) * (b - pi[1][ii]))
        ptn.append(dis)
    ptn = np.array(ptn)  # 此处是插入点离另外输入的16个点的距离
    ptn = (1 / ptn) / np.sum(1 / ptn)  # 此处是权重
    ptn = np.where(ptn > np.max(ptn) * 0.9, ptn, 0)
    aInterpolation = sum(np.multiply(ptn, reArray))
    return aInterpolation


def IDWFinal():
    testArray = np.array([[8, 10], [10, 9]])
    finalArray = np.zeros((200, 200))  # 待扩充矩阵
    fLength, fHigh = finalArray.shape
    tLength, tHigh = testArray.shape
    arraySpace = int(fLength / (tLength + 1))
    for i in range(tLength):
        for j in range(tHigh):
            finalArray[(i + 1) * arraySpace, (j + 1) * arraySpace] = testArray[i, j]

    fIndex = np.nonzero(finalArray)  # 输入点的下标，按行来，从上到下
    for i in range(fLength):
        for j in range(fHigh):
            if finalArray[i, j] == 0:
                finalArray[i, j] = myIDW(i, j, fIndex, testArray)
    finalHSL = (finalArray - np.min(finalArray)) / (np.max(finalArray) - np.min(finalArray))
    finalHSL = 1 - finalHSL
    finalHSL = finalHSL * 0.667
    return finalArray, finalHSL
