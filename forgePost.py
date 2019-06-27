# -*- coding:utf-8 -*-
"""
by:cxn
"""

import requests, os, re, json, base64, time, datetime
import pymysql
import pandas as pd


# 第一步用账号密码连接,获取token
def get_token():
    url = 'https://developer.api.autodesk.com/authentication/v1/authenticate'
    mData = {'client_id': 'Qeul9eD5jp0ySqJrdDnvjEkqmrryZqPO',
             'client_secret': 'KOB1WypAjo6XO3mw', 'grant_type': 'client_credentials'
             , 'scope': 'data:read viewables:read bucket:read bucket:create data:write'}
    header0 = {'Content-Type': 'application/x-www-form-urlencoded'}
    responsed0 = requests.post(url, headers=header0, data=mData)
    return responsed0


# 传入bucketName
def post_bucket_name(token_number):
    tempToken = re.findall('"(.*?)"', token_number)  # responsed0.text
    url1 = 'https://developer.api.autodesk.com/oss/v2/buckets'
    autho = tempToken[3] + ' ' + tempToken[1]
    header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
    mData1 = {'bucketKey': bucketName, 'policyKey': 'transient'}
    responsed1 = requests.post(url1, headers=header, data=json.dumps(mData1))
    return responsed1, autho, mData1, tempToken


# 检查是否在云端建立了bucketName
def check_bucket_name(autho, mData1):
    header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
    url2 = 'https://developer.api.autodesk.com/oss/v2/buckets/' + bucketName + '/details'  # 与第二步的headers和data一样
    responsed2 = requests.get(url2, headers=header, data=json.dumps(mData1))
    return responsed2


# 传文件
def upload_file(autho):
    header3 = {'Authorization': autho, 'Content-Type': 'application/octet-stream',
               'Content-Length': str(os.path.getsize(file_upload))}
    url3 = 'https://developer.api.autodesk.com/oss/v2/buckets/' + bucketName + '/objects/' + file_upload
    with open(file_upload, mode='rb') as fo:
        sn = fo.read(os.path.getsize(file_upload))
        fw = open(file_upload, "wb")
        fw.write(sn)                        # fw的这些操作就是因为读filename3时文件大小会出现问题，重新写一次二进制
        fw.close()
        fw = open(file_upload, "rb")
        responsed3 = requests.put(url3, headers=header3, data=fw)
        fw.close()
        return responsed3


# 用于解urn码
def do_urn(autho, urn_number):
    header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
    tempUrn = re.findall('"(.*?)"', urn_number)    # 用于解码,responsed3.text
    urnEncode = base64.b64encode(tempUrn[3].encode('utf-8'))
    urnEncodeEnd = str(urnEncode, 'utf-8').replace("=", "")
    mData4 = {"input": {"urn": urnEncodeEnd}, "output": {"formats": [{"type": "svf", "views": ["2d", "3d"]}]}}
    url4 = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/job'
    responsed4 = requests.post(url4, headers=header, data=json.dumps(mData4))
    return responsed4, urnEncodeEnd


# 检查模型是否传完,如果报401，则是token问题
def check_model_uploaded(autho, urnEncodeEnd):
    header5 = {'Authorization': autho}
    url5 = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/' + urnEncodeEnd + '/manifest'
    responsed5 = requests.get(url5, headers=header5)
    return responsed5


# 检查是否有文件
def check_file_uploaded(autho):
    header = {'Authorization': autho, 'Content-Type': 'application/json'}  # 好几个用的是这个header
    urnDecode = 'urn:adsk.objects:os.object:' + bucketName + '/' + file_upload
    urnEncode = base64.b64encode(urnDecode.encode('utf-8'))
    urnEncodeEnd = str(urnEncode, 'utf-8').replace("=", "")
    mData4 = {"input": {"urn": urnEncodeEnd}, "output": {"formats": [{"type": "svf", "views": ["2d", "3d"]}]}}
    url4 = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/job'
    responsed = requests.post(url4, headers=header, data=json.dumps(mData4))
    return responsed.status_code, urnEncodeEnd


# 对原有html网页文件进行修改
def change_html_file(viewer_name, tempToken, urnEncodeEnd):
    dir_road = "./"
    for root, dirs, files in os.walk(dir_road):
        for file in files:
            if file == viewer_name:
                with open(os.path.join(root, file), encoding='utf-8', mode='r+') as Html_file:
                    htmlHandle = Html_file.read()
                    assesTokenPatten = re.compile(r'var accessToken =.*')
                    assesTokenReplace = "var accessToken = '" + tempToken[1] + "';"
                    htmlHandle = re.sub(assesTokenPatten, assesTokenReplace, htmlHandle)
                    assesDocumentIdPatten = re.compile(r'var documentId =.*')
                    assesDocumentIdReplace = "var documentId = 'urn:" + urnEncodeEnd + "';"
                    assesDocumentIdOut = re.sub(assesDocumentIdPatten, assesDocumentIdReplace, htmlHandle)  # 最终替换完成的str

                with open(os.path.join(root, file), encoding='utf-8', mode='w+') as newHtml:
                    newHtml.write(assesDocumentIdOut)


def main_code():
    responsed_zero = get_token()
    responsed_one, au_tho, m_data, temp_token = post_bucket_name(responsed_zero.text)
    # responsed_two = check_bucket_name(au_tho, m_data)
    html_states, urn_encode = check_file_uploaded(au_tho)
    if html_states == 201:
        change_html_file(main_viewer_name, temp_token, urn_encode)
    else:
        print(file_upload + ' is uploading... ' + str(datetime.datetime.now()))
        responsed_three = upload_file(au_tho)
        responsed_four, urn_encode = do_urn(au_tho, responsed_three.text)
        # responsed_five = check_model_uploaded(au_tho, urn_encode)
        change_html_file(main_viewer_name, temp_token, urn_encode)
        time.sleep(10)
        print(file_upload + ' is uploaded ' + str(datetime.datetime.now()))
    print(main_viewer_name + ' is loaded ' + str(datetime.datetime.now()))


def forgeTableData(ipString):
    connected = pymysql.connect(host=ipString, port=3306,user='cxn',password='123456',db='unitymonitor',charset='utf8mb4')
    # 使用cursor()方法获取操作游标
    cur = connected.cursor()
    # 1.查询操作  # 编写sql 查询语句  user 对应我的表名
    sql = "select * from assetlist_test"
    try:
        cur.execute(sql)
        # 执行sql语句
        results = cur.fetchall()    # 返回结果为tuple,可直接转为dataframe
        unity_df = pd.DataFrame(list(results))
    except Exception as e:
        raise e
    finally:
            connected.close()  # 关闭连接
    return unity_df


bucketName = 'bucket_305'   # 全局变量
file_upload = 'tested.rvt'  # 测试用文件名
main_viewer_name = "viewer.js"    # 主页文件名
# main_code()
