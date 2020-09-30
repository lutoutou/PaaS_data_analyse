import sys
import json
from flask import Flask, request
from flask_restful import Resource, Api
from pandahouse import read_clickhouse
import datetime


app = Flask(__name__)
api = Api(app)

if len(sys.argv)==6:
    host, port, password, expose_host, expose_port = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    connection = {'host':'http://'+host+':'+port+'/',\
                  'password':password}
elif len(sys.argv)==5:
    host, port, expose_host, expose_port = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    connection = {'host':'http://'+host+':'+port+'/'}

# 每一项的标题
titles = ["Time", "Type", "Object", "Reason", "Message"]

# 用于存储sql语句
class sqlSentence(object):
    def __init__(self):
        self.sql = "select toDateTime(substring(visitParamExtractString(metadata, 'creationTimestamp'), 1, 19)) as Time, eventType, visitParamExtractString(involvedObject, 'kind') AS kind, reason, message, visitParamExtractString(involvedObject, 'name') AS name \
                        from datagather.paas_gather_event_logs_all "
        self.sql_search_by_name = " visitParamExtractString(involvedObject, 'name') like "
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

@app.route('/analyseData', methods=['GET'])
def hello():
    key_word = request.args.get('key_word')
    name = request.args.get('name')
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
        if key_word:
            key_word = key_word.lower()
        sql += " where " + sql_search_by_all_deployment_related
        sql += " and " + sql_search_by_name
        sql += "'"+name+"%'"
        if key_word:
            sql += " and ("
            sql += sql_search_by_type + "'%"+key_word+"%'"
            sql += sql_search_by_kind + "'%"+key_word+"%'"
            sql += sql_search_by_reason + "'%"+key_word+"%'"
            sql += sql_search_by_message + "'%"+key_word+"%'"
            sql += ")"
        sql += ";"
        print(sql)
        
        df = read_clickhouse(sql, connection=connection)
        print(df)

        data = [{
            titles[0]:row[0].strftime('%Y-%m-%d %H:%M:%S'),
            titles[1]:row[1],
            titles[2]:row[2]+":"+row[5],
            titles[3]:row[3],
            titles[4]:row[4]
        } for row in df.values]

    except Exception as r:
        print(r)

    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True, host=expose_host, port=expose_port)
    # 为防止和其他主机号端口号冲突，因此将主机号设为0.0.0.0支持所有主机号的监听