import hashlib
import json
import jsonpath
import requests


# 获取token
def get_user_token(username, password):
    url = "https://enweb.test.seewo.com/api.json?actionName=USER_AUTH"

    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }

    params = {
        'username': username,
        'password': password
    }

    value = {}

    params = json.dumps(params)
    response = requests.post(url, data=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..error_code')[0]
    value['error_code'] = error_code
    if error_code == 0:
        token = jsonpath.jsonpath(data, '$..token')[0]
        value['token'] = token
    else:
        message = jsonpath.jsonpath(data, '$..message')[0]
        value['message'] = message
    return value

# 获取有希沃资源管理后台权限用户的token
def get_resource_user_token():
    url = "https://enweb.test.seewo.com/api.json?actionName=USER_AUTH"

    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }

    params = {
        'username': '13172495395',
        'password': '36737be16f6b5bf21f230856c187c38b'
    }

    value = {}

    params = json.dumps(params)
    response = requests.post(url, data=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..error_code')[0]
    value['error_code'] = error_code
    if error_code == 0:
        token = jsonpath.jsonpath(data, '$..token')[0]
        value['token'] = token
    else:
        message = jsonpath.jsonpath(data, '$..message')[0]
        value['message'] = message
    return value


# 获取资源包（课件、教案），并返回cid、uid
def get_resource(token):
    url = "http://edu.test.seewo.com/coursewarebank/api/v1/resource/pack/download"

    header = {
        "Cookie": "x-auth-app=EasiNote5;x-auth-token=" + token,
        "Content-Type": "application/json"
    }

    params = {
        "uid": "drwbqp321u3mvf45tha02oilj9xg57s6"
    }

    value = {}

    response = requests.post(url, headers=header, json=params)
    jsondata = json.loads(response.text)
    value['code'] = jsondata['error_code']
    if jsondata['error_code'] == 0:
        for i in jsondata['data']['resList']:
            if 'otherInfo' in i:
                if 'bindCIdList' in i['otherInfo']:
                    value['cid'] = i['otherInfo']['bindCIdList'][0]
                    value['uid'] = i['otherInfo']['uid']
    else:
        value['message'] = jsondata['message']

    return value


# 拼接sql
def getSqlCids(cIds):
    sqlCids = ''
    for index in range(len(cIds)):
        if index == 0:
            sqlCids = sqlCids + '('
            sqlCids = sqlCids + '\'' + cIds[index] + '\'' + ','
        elif index == (len(cIds) - 1):
            sqlCids = sqlCids + '\'' + cIds[index] + '\''
            sqlCids = sqlCids + ')'
        else:
            sqlCids = sqlCids + '\'' + cIds[index] + '\'' + ','
    return sqlCids

# md5加密
def getMd5(str):
    # 创建md5对象
    m = hashlib.md5()

    b = str.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()

    return str_md5
