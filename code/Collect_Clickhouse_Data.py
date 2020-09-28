import sys
import json
from flask import Flask
from flask_restful import Resource, Api
from clickhouse_driver import Client
import datetime


app = Flask(__name__)
api = Api(app)

# System arguments: the first argument should be host, and the second should be port number.
# System arguments: the third argument should be the host expose to visit, and the forth should be port number expose with host to visit

host, port, expose_host, expose_port = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
client = Client(host=host, port=port)

# 每一项的标题
titles = ["Time", "Type", "Object", "Reason", "Message"]

# 用于存储sql语句
class sqlSentence(object):
    def __init__(self):
        self.sql = "select toDateTime(substring(visitParamExtractString(metadata, 'creationTimestamp'), 1, 19)) as Time, eventType, visitParamExtractString(involvedObject, 'kind') AS kind, reason, message, visitParamExtractString(involvedObject, 'name') AS name \
                        from datagather.paas_gather_event_logs_all "
        self.sql_search_by_name = " visitParamExtractString(involvedObject, 'name')="
        self.sql_search_by_type = " lower(eventType) like "
        self.sql_search_by_kind = " or lower(kind) like "
        self.sql_search_by_reason = " or lower(reason) like "
        self.sql_search_by_message = " or lower(message) like "
        self.sql_search_by_all_deployment_related = " (visitParamExtractString(involvedObject, 'kind') = 'Deployment' \
            or visitParamExtractString(involvedObject, 'kind') = 'ReplicaSet'\
            or visitParamExtractString(involvedObject, 'kind') = 'Pod')"

'''
输出格式为list, list中每个元素为如下json:
{
    "Time": "2020-09-25 09:01:02",
    "Type": "Normal",
    "Object": "Pod: nginx-resource-7c797cdc9f-rmrkn",
    "Reason": "Created",
    "Message": "Created container nginx"
}
'''

# 用于测试的数据
# name = "coc2-common-77b9587fdc"
# key_word = "warn"

# 检索未加入任何参数，则搜索全部deplpyment信息
class analyseData_all(Resource):
    def get(self):
        # 返回的结果
        data = []
        sql_result = []
        sql_sentence = sqlSentence()
        sql = sql_sentence.sql
        sql_search_by_all_deployment_related = sql_sentence.sql_search_by_all_deployment_related
        try:
            sql += " where " + sql_search_by_all_deployment_related
            sql += ";"
            print(sql)
            sql_result += client.execute(sql)
            for row in sql_result:
                temp_dict = {}
                temp_dict[titles[0]] = row[0].strftime('%Y-%m-%d %H:%M:%S')
                temp_dict[titles[1]] = row[1]
                temp_dict[titles[2]] = row[2]+":"+row[5]
                temp_dict[titles[3]] = row[3]
                temp_dict[titles[4]] = row[4]
                data.append(temp_dict)
        except Exception as r:
            print(r)

        return data

class analyseData_keyWord(Resource):
    def get(self, key_word):
        sql_sentence = sqlSentence()
        sql = sql_sentence.sql
        sql_search_by_type = sql_sentence.sql_search_by_type
        sql_search_by_kind = sql_sentence.sql_search_by_kind
        sql_search_by_reason = sql_sentence.sql_search_by_reason
        sql_search_by_message = sql_sentence.sql_search_by_message
        key_word = key_word.lower()
        # 返回的结果
        data = []
        sql_result = []
        try:
            sql += "where "
            sql += sql_search_by_type + "'%"+key_word+"%'"
            sql += sql_search_by_kind + "'%"+key_word+"%'"
            sql += sql_search_by_reason + "'%"+key_word+"%'"
            sql += sql_search_by_message + "'%"+key_word+"%'"
            sql += ";"
            print(sql)
            sql_result += client.execute(sql)
            for row in sql_result:
                temp_dict = {}
                temp_dict[titles[0]] = row[0].strftime('%Y-%m-%d %H:%M:%S')
                temp_dict[titles[1]] = row[1]
                temp_dict[titles[2]] = row[2]+":"+row[5]
                temp_dict[titles[3]] = row[3]
                temp_dict[titles[4]] = row[4]
                data.append(temp_dict)
            
        except Exception as r:
            print(r)

        return data

class analyseData_name(Resource):
    def get(self, namelist):
        sql_sentence = sqlSentence()
        sql = sql_sentence.sql
        sql_search_by_name = sql_sentence.sql_search_by_name
        sql_search_by_all_deployment_related = sql_sentence.sql_search_by_all_deployment_related
        # 返回的结果
        data = []
        sql_result = []
        try:
            namelist = json.loads(namelist)
            sql += "where " + sql_search_by_all_deployment_related
            sql += " and " + sql_search_by_name
            for name in namelist:
                sql += "'"+name+"'"
                sql += ";"
                print(sql)
                sql_result += client.execute(sql)
            for row in sql_result:
                temp_dict = {}
                temp_dict[titles[0]] = row[0].strftime('%Y-%m-%d %H:%M:%S')
                temp_dict[titles[1]] = row[1]
                temp_dict[titles[2]] = row[2]+":"+row[5]
                temp_dict[titles[3]] = row[3]
                temp_dict[titles[4]] = row[4]
                data.append(temp_dict)
        except Exception as r:
            print(r)

        return data

class analyseData_keyWord_name(Resource):
    def get(self, key_word, namelist):
        sql_sentence = sqlSentence()
        sql = sql_sentence.sql
        sql_search_by_name = sql_sentence.sql_search_by_name
        sql_search_by_type = sql_sentence.sql_search_by_type
        sql_search_by_kind = sql_sentence.sql_search_by_kind
        sql_search_by_reason = sql_sentence.sql_search_by_reason
        sql_search_by_message = sql_sentence.sql_search_by_message
        sql_search_by_all_deployment_related = sql_sentence.sql_search_by_all_deployment_related
        # 返回的结果
        data = []
        sql_result = []
        try:
            key_word = key_word.lower()
            namelist = json.loads(namelist)
            sql += " where " + sql_search_by_all_deployment_related
            sql += " and " + sql_search_by_name
            for name in namelist:
                sql += "'"+name+"'"
                sql += " and ("
                sql += sql_search_by_type + "'%"+key_word+"%'"
                sql += sql_search_by_kind + "'%"+key_word+"%'"
                sql += sql_search_by_reason + "'%"+key_word+"%'"
                sql += sql_search_by_message + "'%"+key_word+"%'"
                sql += ")"
                sql += ";"
                print(sql)
                sql_result += client.execute(sql)
            for row in sql_result:
                temp_dict = {}
                temp_dict[titles[0]] = row[0].strftime('%Y-%m-%d %H:%M:%S')
                temp_dict[titles[1]] = row[1]
                temp_dict[titles[2]] = row[2]+":"+row[5]
                temp_dict[titles[3]] = row[3]
                temp_dict[titles[4]] = row[4]
                data.append(temp_dict)
        except Exception as r:
            print(r)

        return data

# 链接1：不加任何参数查询deployment的event日志
api.add_resource(analyseData_all, '/analyseData_all')
# 链接2：只有key word的条件下查询所有deployment的日志
api.add_resource(analyseData_keyWord, '/analyseData_keyWord/<string:key_word>')
# 链接3：只有deployment相关机器或主机号的情况下查询event日志
api.add_resource(analyseData_name, '/analyseData/<string:namelist>')
# 链接4：利用deployment名称或rs或pod加关键字查询event日志
api.add_resource(analyseData_keyWord_name, '/analyseData/<string:namelist>/<string:key_word>')

if __name__ == '__main__':
    app.run(debug=True, host=expose_host, port=expose_port)
    # 为防止和其他主机号端口号冲突，因此将主机号设为0.0.0.0支持所有主机号的监听