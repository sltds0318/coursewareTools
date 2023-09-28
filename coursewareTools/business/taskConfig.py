import jsonpath
import requests
import json

from business.userConfig import get_user_token, get_resource
from business.dbConfig import get_courseware_version, get_resource_library, get_en_cw_test, \
    get_seewo_school_teaching_plan
from business.dbConfig import get_resource_center
from business.dbConfig import get_encloud_thumbnail

url = "http://xxl-job.test.gz.cvte.cn/seewo-xxl-job-admin/jobinfo/trigger"

headers = {
    'cookie': 'XXL_JOB_LOGIN_IDENTITY=6333303830376536353837616465323835626137616465396638383162336437'
}


# 执行定时任务
def perform_task(id):
    # 1913 上架课件      1527 课件库定时上传课件任务
    params = {
        'id': id
    }

    response = requests.post(url, headers=headers, params=params)
    DataNode = json.loads(response.text)

    return DataNode


# 获取课件最大版本数
def get_courseware_maxVersion(cid):
    conn = get_courseware_version('courseware_version')
    cursor = conn.cursor()
    sql = "SELECT MAX(c_version) FROM t_courseware_version WHERE t_courseware_c_id =" + '\'' + cid + '\''

    cursor.execute(sql)
    maxVersion = cursor.fetchone()

    return maxVersion


# 获取t_thumbnail_task表中的截图进度
def get_thumbnail(cid):
    # 连接mysql
    conn = get_encloud_thumbnail('encloud_thumbnail')

    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM t_thumbnail_task WHERE c_courseware_id = " + '\'' + cid + '\'' + "AND c_priority = 99"

    # 执行sql语句
    cursor.execute(sql)

    # 使用 fetchone() 方法获取单条数据;使用 fetchall() 方法获取所有数据
    data = cursor.fetchall()

    conn.close()

    return data


# 上传课件
def upload_courseware(cid, maxVersion, token, indexId, cwName, tagNames, description, type, referencedList):
    url = "http://edu.test.seewo.com/coursewarebank/api/v1/c/upload"

    headers = {
        'cookie': 'x-auth-token=' + token + ';x-auth-app=EasiNet',
        'Content-Type': 'application/json'
    }

    if type == 0:
        params = [{
            "cId": cid,
            "cVersion": maxVersion,
            "indexId": indexId,
            "cwName": cwName,
            "tagNames": tagNames,
            "description": description,
            "type": type
        }]
    elif type == 1:
        params = [{
            "cId": cid,
            "cVersion": maxVersion,
            "indexId": indexId,
            "cwName": cwName,
            "tagNames": tagNames,
            "description": description,
            "type": type,
            "referencedList": referencedList
        }]

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..error_code')[0]
    message = jsonpath.jsonpath(data, '$..message')[0]
    value['error_code'] = error_code
    value['message'] = message
    return value


# 上传教案
def upload_plan(planUid, maxVersion, token, indexId, PlanName, tagNames, description, type):
    url = "http://edu.test.seewo.com/coursewarebank/api/v1/teaching/plan/upload"

    headers = {
        'cookie': 'x-auth-token=' + token + ';x-auth-app=EasiNet',
        'Content-Type': 'application/json'
    }

    params = {
        "planUid": planUid,
        "version": maxVersion,
        "indexId": indexId,
        "name": PlanName,
        "teachingPlanTypeUid": type,
        "tagNames": tagNames,
        "description": description
    }

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..error_code')[0]
    message = jsonpath.jsonpath(data, '$..message')[0]
    value['error_code'] = error_code
    value['message'] = message
    return value

# 判断截图表是否存在该课件的截图数据
def is_thumbnail(cid):
    print('正在判断t_thumbnail_task表是否存在该课件：' + cid + '\t数据')
    while True:
        # perform_task(1913)
        # perform_task(1527)
        # print(perform_task(1913))
        print(perform_task(1527))
        thumbnail = get_thumbnail(cid)
        if thumbnail:
            print('t_thumbnail_task已存在该课件：' + cid + '\t数据，开始截图')
            break

# 判断截图进度是否为100
def get_progress(cid):
    # 获取课件状态
    conn = get_resource_library('resource_library')
    cursor = conn.cursor()
    sql = "SELECT * FROM t_cb_c_upload_record_detail WHERE c_c_id  = " + '\'' + cid + '\''
    while True:
        # 执行sql语句
        cursor.execute(sql)

        # 使用 fetchone() 方法获取单条数据;使用 fetchall() 方法获取所有数据
        data = cursor.fetchall()

        # 有课件上传就开始执行定时任务
        if data:
            # 1913 上架课件      1527 课件库定时上传课件任务
            json = perform_task(1913)
            json1 = perform_task(1527)

            print('上架课件', json)
            print('课件库定时上传课件任务', json1)

            thumbnail = get_thumbnail(cid)

            if thumbnail:
                a = thumbnail[0][6]
                while True:
                    thumbnail = get_thumbnail(cid)
                    b = thumbnail[0][6]
                    if a != b:
                        a = b
                        print('目前截图进度：', thumbnail[0][6])
                    if thumbnail[0][6] == 100:
                        break
                break
    conn.close()
    return '截图进度已达100'


# 判断课件截图是否已上传完成（前提条件：课件截图进度已达100）
def get_thumbnail_finish(cid):
    origin_uid = 'easinote-' + cid + '.5'
    # 获取课件状态
    conn = get_resource_library('resource_library')
    conn1 = get_resource_center('resource_center')
    cursor = conn.cursor()
    cursor1 = conn1.cursor()
    sql = "SELECT * FROM t_cb_c_upload_record_detail WHERE c_c_id  = " + '\'' + cid + '\''
    sql1 = "UPDATE t_courseware SET algorithm_status = 1 WHERE origin_uid = " + '\'' + origin_uid + '\''

    while True:
        # 执行sql语句
        cursor.execute(sql)
        data = cursor.fetchall()
        if data[0][2] == 'UPLOADED':
            print('课件当前状态：', data[0][2])
            print('课件截图已上传完成')
            break
        else:
            print('课件当前状态：', data[0][2])

    # 课件截图上传完成就通过机器审核
    cursor1.execute(sql1)

    # 提交sql
    conn1.commit()
    print('成功修改t_courseware表中', cursor1.rowcount, '条数据')

    conn.close()
    conn1.close()

    return '课件已通过机器审核'


# 获取课件uid
def get_courseware_uid(cid, maxVersion):
    maxVersion = str(maxVersion)
    originUid = 'easinote-' + cid + '.' + maxVersion

    # 连接mysql
    conn = get_resource_center('resource_center')

    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM t_courseware WHERE origin_uid = " + '\'' + originUid + '\''

    # 执行sql语句
    cursor.execute(sql)

    # 使用 fetchone() 方法获取单条数据;使用 fetchall() 方法获取所有数据
    data = cursor.fetchall()

    conn.close()

    return data

# 获取教案uid
def get_plan_uid(origin_uid):
    # 连接mysql
    conn = get_resource_center('resource_center')

    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM t_teaching_plan WHERE origin_uid = " + '\'' + origin_uid + '\''

    # 执行sql语句
    cursor.execute(sql)

    # 使用 fetchone() 方法获取单条数据;使用 fetchall() 方法获取所有数据
    data = cursor.fetchall()

    conn.close()

    return data



# 课件通过审核
def courseware_approve(uid, token):
    url = "http://resource.test.seewo.com/api/admin/v1/resource/courseware/approve"

    headers = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }

    params = {
        "notNeedChapterIds": [],
        "ids": [uid],
        "reason": "",
        "auditUids": [],
        "auditType": ""
    }

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    data = jsonpath.jsonpath(data, '$..data')[0]
    value['code'] = error_code
    value['errorMsg'] = message
    value['data'] = data

    return value


# 课件审核不通过
def courseware_disapprove(uid, token, auditUid):
    url = "http://resource.test.seewo.com/api/admin/v1/resource/courseware/disapprove"

    headers = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }

    params = {
        "notNeedChapterIds": [],
        "ids": [uid],
        "reason": "",
        "auditUids": [auditUid],
        "auditType": 0
    }

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    data = jsonpath.jsonpath(data, '$..data')[0]
    value['code'] = error_code
    value['errorMsg'] = message
    value['data'] = data

    return value


# 课件上架
def courseware_shelf(uid, token):
    url = "http://resource.test.seewo.com//api/admin/v1/resource/courseware/shelf"

    headers = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }

    params = {
        "ids": [uid],
        "reason": ""
    }

    value = {}

    response = requests.put(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    value['code'] = error_code
    value['errorMsg'] = message

    return value

# 教案跑到资源审核后台就通过机器审核
def plan_pass(uid):
    conn = get_resource_center('resource_center')
    cursor = conn.cursor()
    sql = "SELECT * FROM t_teaching_plan WHERE origin_uid  = " + '\'' + uid + '\''
    sql1 = "UPDATE t_teaching_plan SET algorithm_status = 1 WHERE origin_uid = " + '\'' + uid + '\''
    while True:
        cursor.execute(sql)
        data = cursor.fetchall()
        # 判断教案是否已跑到希沃资源管理后台
        if data:
            print('教案已跑到希沃资源管理后台')
            break

    cursor.execute(sql1)
    # 提交sql
    conn.commit()
    print('成功修改t_teaching_plan表中', cursor.rowcount, '条数据')

    conn.close()

    return '教案已通过机器审核'

# 教案通过人工审核审核
def plan_approve(uid, token):
    url = "https://resource.test.seewo.com/api/resource/approve"

    headers = {
        'Content-Type': 'application/json',
        'cookie': 'x-token=' + token
    }

    params = {
        "notNeedChapterIds": [],
        "ids": [uid],
        "reason": "",
        "resourceType": "teachingPlan"
    }

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    data = jsonpath.jsonpath(data, '$..data')[0]
    value['code'] = error_code
    value['errorMsg'] = message
    value['data'] = data

    return value

# 教案人工审核不通过
def plan_disapprove(uid, token, auditUid):
    url = "https://resource.test.seewo.com/api/resource/disapprove"

    headers = {
        'Content-Type': 'application/json',
        'cookie': 'x-token=' + token
    }

    params = {
        "ids": [uid],
        "reason": "",
        "auditUids": [auditUid],
        "auditType": 0,
        "resourceType": "teachingPlan"
    }

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    data = jsonpath.jsonpath(data, '$..data')[0]
    value['code'] = error_code
    value['errorMsg'] = message
    value['data'] = data

    return value

# 教案上架
def plan_shelf(uid, token):
    url = "https://resource.test.seewo.com/api/shelf/resource/batchOnShelf"

    headers = {
        'Content-Type': 'application/json',
        'cookie': 'x-token=' + token
    }

    params = {
        "ids": [uid],
        "reason": "",
        "resourceType": "teachingPlan"
    }

    value = {}

    response = requests.put(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    value['code'] = error_code
    value['errorMsg'] = message

    return value


# 获取课件/教案的关联章节
def get_chapters(uid, token, resourceType):
    url = "https://resource.test.seewo.com/api/resource/" + uid + "/chapters?resourceType=" + resourceType

    headers = {
        'cookie': "x-token=" + token
    }

    value = {}

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    data = jsonpath.jsonpath(data, '$..data')[0]
    value['code'] = error_code
    value['errorMsg'] = message
    value['data'] = data

    return value

# 修改课件/教案的关联章节
def update_chapters(uid, token, newChapterId, resourceType):
    # 获取课件/教案的关联章节
    chapters = get_chapters(uid, token, resourceType)
    oldChapterId = chapters.get('data')[0].get('seewoChapterId')

    url = "https://resource.test.seewo.com/api/resource/" + uid + "/chapters"

    headers = {
        'Content-Type': 'application/json',
        'cookie': "x-token=" + token
    }

    params = {
        "resourceType": resourceType,
        "oldChapterId": oldChapterId,
        "newChapterId": newChapterId
    }

    value = {}

    response = requests.post(url, json=params, headers=headers)
    data = json.loads(response.text)
    error_code = jsonpath.jsonpath(data, '$..code')[0]
    message = jsonpath.jsonpath(data, '$..errorMsg')[0]
    data = jsonpath.jsonpath(data, '$..data')[0]
    value['code'] = error_code
    value['errorMsg'] = message
    value['data'] = data

    return value


# 根据用户账号、用户密码获取课件、教案
def get_courseware_word(username, password, num):

    res = {}

    # 连接mysql
    conn = get_en_cw_test('en_cw_test')
    conn1 = get_courseware_version('courseware_version')
    conn2 = get_seewo_school_teaching_plan('seewo_school_teaching_plan')

    # 获取token
    values = get_user_token(username, password)
    if values.get('error_code') == 0:
        token = values.get('token')
        print('token获取成功', values.get('token'))
    else:
        res['message'] = '获取token失败，原因：'+ values.get('message')
        return res

    print('正在获取', num, '份教案与课件到该账号：', username)

    cids = []
    uids = []

    # 获取教案、课件并获取教案、课件id
    for index in range(num):
        values1 = get_resource(token)
        if values1.get('code') == 0:
            print('第', index, '课件获取成功：', values1.get('cid'))
            print('第', index, '教案获取成功：', values1.get('uid'))
            cids.append(values1.get('cid'))
            uids.append(values1.get('uid'))
        else:
            res['message'] = '第' + str(index) + '课件与教案获取失败，原因：' + values1.get('message')
            return res

    sqls = []
    sql1s = []
    sql2s = []

    for index in range(num):
        sql = "UPDATE t_courseware SET c_size = 2200000,c_version = 5 WHERE c_id = " + '\'' + cids[index] + '\''
        sql1 = "UPDATE t_courseware_version " \
               "SET c_size = 2200000,c_version = 5,c_server_time=DATE_SUB(NOW(),INTERVAL 1 DAY) " \
               "WHERE t_courseware_c_id =" + '\'' + cids[index] + '\'' \
                                                                  "and c_version = (select max(c_version) from t_courseware_version " \
                                                                  "where t_courseware_c_id =" + '\'' + cids[
                   index] + '\' )'
        sql2 = "UPDATE t_teacher_teaching_plan_content_version SET c_version = 5 WHERE c_teaching_plan_id = (SELECT c_id FROM `t_teacher_teaching_plan_info` WHERE c_uid = " + '\'' + \
               uids[index] + '\' )'
        sqls.append(sql)
        sql1s.append(sql1)
        sql2s.append(sql2)

    cursor = conn.cursor()
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    # 执行sql语句
    for index in range(num):
        cursor.execute(sqls[index])
        cursor1.execute(sql1s[index])
        cursor2.execute(sql2s[index])

    # 提交sql
    conn.commit()
    conn1.commit()
    conn2.commit()
    print('已获取', num, '份教案与课件到该账号：', username)

    conn.close()
    conn1.close()
    conn2.close()

    message = '已获取' + str(num) + '份教案与课件到该账号：' + username
    res['message'] = message
    res['courseware'] = cids
    res['teacherPlan'] = uids
    return res

# 获取学科教育下学科学段
def get_school_subject():
    url = "http://easinote.test.seewo.com/courseroom/apis?actionName=GET_SCHOOL_SUBJECT_VERSION"

    response = requests.get(url)
    data = json.loads(response.text)

    return data


# 获取特殊教育下学科学段
def get_special_education():
    url = "http://easinote.test.seewo.com/courseroom/apis?actionName=GET_UPLOAD_SPECIAL_EDUCATION_VERSION"

    response = requests.get(url)
    data = json.loads(response.text)

    return data

# 获取专题教育下的学科学段
def get_theme_education():
    url = "http://easinote.test.seewo.com/courseroom/apis?actionName=GET_THEME_COURSEWARE_TREE"

    response = requests.get(url)
    data = json.loads(response.text)

    return data

def get_professional_education():
    url = "http://easinote.test.seewo.com/courseroom/apis?actionName=GET_UPLOAD_PROFESSIONAL_EDUCATION_VERSION"

    response = requests.get(url)
    data = json.loads(response.text)

    return data