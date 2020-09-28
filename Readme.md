使用方法：
step1: 启动服务，在启动docker容器时输入系统参数：
例如 python3 Collcet_Clickhouse_Data.py 127.0.0.1 9000 127.0.0.1 5000
第一第二个参数分别为连接clickhouse数据库的主机地址和端口号
后两个参数为接口需要暴露出来的主机号和端口号

step2: 启动服务后，可访问链接获取数据

链接1：不加任何参数查询deployment的event日志
http://<host:port>/analyseData_all
链接2：只有key word的条件下查询所有deployment的日志
http://<host:port>/analyseData_keyWord/<string:key_word>
链接3：只有deployment相关机器或主机号的情况下查询event日志
http://<host:port>/analyseData/<string:namelist>
链接4：利用deployment名称或rs或pod加关键字查询event日志
http://<host:port>/analyseData/<string:namelist>/<string:key_word>

数据为json格式，一个list中元素如下所示
{
    "Time": "2020-09-25 09:01:02",
    "Type": "Normal",
    "Object": "Pod: nginx-resource-7c797cdc9f-rmrkn",
    "Reason": "Created",
    "Message": "Created container nginx"
}
