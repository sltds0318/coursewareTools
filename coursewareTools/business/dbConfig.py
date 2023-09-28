import pymysql


def get_en_cw_test(db):
    connect = pymysql.connect(host="encloud-test-mysql-master-3472.ot1.gz.paas.cvtecs.com",
                              port=3472,
                              user="en_cw_test",
                              password="4xvolTTp0bc",
                              db=db,
                              charset="utf8")
    return connect


def get_courseware_version(db):
    connect = pymysql.connect(host="sr-test-tidb-master-performance.sr.cvte.cn",
                              port=3339,
                              user="courseware_version",
                              password="6k5CYWPx382",
                              db=db,
                              charset="utf8")
    return connect


def get_encloud_test(db):
    connect = pymysql.connect(host="encloud-test-mysql-master-3472.ot1.gz.paas.cvtecs.com",
                              port=3472,
                              user="encloud_test",
                              password="6k5CYWPx2W",
                              db=db,
                              charset="utf8")
    return connect

def get_resource_library(db):
    connect = pymysql.connect(host="encloud-test-mysql-master-3472.ot1.gz.paas.cvtecs.com",
                              port=3472,
                              user="resource_library",
                              password="Yn~42EhX",
                              db=db,
                              charset="utf8")
    return connect


def get_encloud_thumbnail(db):
    connect = pymysql.connect(host="encloud-test-mysql-master-3472.ot1.gz.paas.cvtecs.com",
                              port=3472,
                              user="encloud_thumbnail",
                              password="6k5CYWdsfdsaW",
                              db=db,
                              charset="utf8")
    return connect


def get_resource_center(db):
    connect = pymysql.connect(host="sr-test-mysql-master-1.gz.cvte.cn",
                              port=3306,
                              user="seewo",
                              password="seewo@cvte",
                              db=db,
                              charset="utf8")
    return connect


def get_seewo_school_teaching_plan(db):
    connect = pymysql.connect(host="sr-test-mysql8-3-master.sr.cvte.cn",
                              port=3475,
                              user="seewo_school_teaching_plan",
                              password="Pass4teaching_plan2021",
                              db=db,
                              charset="utf8")
    return connect