from dbConfig import get_en_cw_test, get_courseware_version, get_seewo_school_teaching_plan
from userConfig import get_user_token, get_resource
from taskConfig import get_progress, get_thumbnail_finish, get_courseware_maxVersion, upload_courseware, \
    get_courseware_uid, courseware_approve, courseware_shelf, courseware_disapprove

# 连接mysql
conn = get_en_cw_test('en_cw_test')
conn1 = get_courseware_version('courseware_version')
conn2 = get_seewo_school_teaching_plan('seewo_school_teaching_plan')

username = '13172495395'
# 填写加密过的密码
password = '36737be16f6b5bf21f230856c187c38b'
# 36737be16f6b5bf21f230856c187c38b   hujiang520.
# e10adc3949ba59abbe56e057f20f883e   123456

# 需要获取的教案与课件数
num = 5

# 获取token
values = get_user_token(username, password)
if values.get('error_code') == 0:
    token = values.get('token')
    print('token获取成功', values.get('token'))
else:
    print('获取token失败，原因：', values.get('message'))
    quit()

print('正在获取', num, '份教案与课件到该账号：', username)

cids = []
uids = []

# 获取教案、课件并获取教案、课件id
for index in range(num):
    values1 = get_resource(token)
    if values1.get('code') == '000000':
        print('第', index, '课件获取成功：', values1.get('cId'))
        print('第', index, '教案获取成功：', values1.get('uid'))
        cids.append(values1.get('cId'))
        uids.append(values1.get('uid'))
    else:
        print('第', index, '课件与教案获取失败，原因：', values1.get('message'))
        quit()

sqls = []
sql1s = []
sql2s = []

for index in range(num):
    sql = "UPDATE t_courseware SET c_size = 2200000,c_version = 5 WHERE c_id = " + '\'' + cids[index] + '\''
    sql1 = "UPDATE t_courseware_version " \
           "SET c_size = 2200000,c_version = 5,c_server_time=DATE_SUB(NOW(),INTERVAL 1 DAY) " \
           "WHERE t_courseware_c_id =" + '\'' + cids[index] + '\'' \
              "and c_version = (select max(c_version) from t_courseware_version " \
              "where t_courseware_c_id =" + '\'' + cids[index] + '\' )'
    sql2 = "UPDATE t_teacher_teaching_plan_content_version SET c_version = 5 WHERE c_teaching_plan_id = (SELECT c_id FROM `t_teacher_teaching_plan_info` WHERE c_uid = " + '\'' + uids[index] + '\' )'
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