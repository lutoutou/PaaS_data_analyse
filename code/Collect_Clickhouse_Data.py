import sys
import json
from flask import Flask
from flask_restful import Resource, Api
from clickhouse_driver import Client
import pandas as pd
import matplotlib.pyplot as plt
import datetime


app = Flask(__name__)
api = Api(app)

# System arguments: the first argument should be host, and the second should be port number.
# System arguments: the third argument should be the host expose to visit, and the forth should be port number expose with host to visit

host, port, expose_host, expose_port = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
client = Client(host=host, port=port)
    
class analyseData(Resource):
    # 方法的参数为分区名称和集群名称
    def get(self, clustername, namespaceName, namelist):
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
        # 每一项的标题
        titles = ["Time", "Type", "Object", "Reason", "Message"]
        # 返回的结果
        data = []
        namelist = json.loads(namelist)
        try:
            for name in namelist:
                sql = "select toDateTime(substring(visitParamExtractString(metadata, 'creationTimestamp'), 1, 19)) as Time, eventType, visitParamExtractString(involvedObject, 'kind') AS kind, reason, message \
                        from datagather.paas_gather_event_logs_all \
                        where clustername='"+clustername+"' \
                            and visitParamExtractString(metadata, 'namespace')='"+namespaceName+"' \
                            and  visitParamExtractString(involvedObject, 'name')='"+name+"';"
                sql_result = client.execute(sql)
                for row in sql_result:
                    temp_dict = {}
                    temp_dict[titles[0]] = row[0].strftime('%Y-%m-%d %H:%M:%S')
                    temp_dict[titles[1]] = row[1]
                    temp_dict[titles[2]] = row[2]+":"+name
                    temp_dict[titles[3]] = row[3]
                    temp_dict[titles[4]] = row[4]
                    data.append(temp_dict)
        except Exception as r:
            print(r)

        return data

api.add_resource(analyseData, '/name/<string:clustername>/<string:namespaceName>/<string:namelist>')

if __name__ == '__main__':
    app.run(debug=True, host=expose_host, port=expose_port)
    # 为防止和其他主机号端口号冲突，因此将主机号设为0.0.0.0支持所有主机号的监听