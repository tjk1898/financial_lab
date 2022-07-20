# -*- encoding: utf-8 -*-
# !/usr/bin/env python
"""
@File    : MysqlUtils.py
@Time    : 2021/04/20 19:19
@Author  : Parker
@Version : 2.0
@Contact : 1251633579@qq.com
@Desc    :
Mysql的工具包：方便利用python操作数据库
TO-DO:
池   √
默认连接数据库，但提供接口可修改    √
创建当前数据库的数据表 ok
insert增加、插入数据-一条    ok
insert增加、插入数据-多条    ok
update修改更新一条 ok
update修改更新多条 ok
select查询    √
select查询统计  √
delete删除表数据 √
truncate删除表 √
参考：
https://47.96.85.49/!/#Hr/view/head/trunk/code/jiangxi/CustomUtils/MysqlConnect.py
https://blog.csdn.net/ITBigGod/article/details/103134635
"""

import pandas as pd
import re
import sys
import pymysql
from dbutils.pooled_db import PooledDB
from conf import config
from utils.logger import log


class MysqlUtils(object):
    def __init__(self, ip: str = None, port: int = None, db=None, user=None, password=None):
        """
        初始化，默认连接Conf包内config的配置；如需连接不同数据库、表，需要传入db等配置
        :param ip: str
        :param port: int
        :param db: default
        :param user: default
        :param password: default
        """
        self.__mysql_ip = config.mysql_ip if ip is None else ip
        self.__mysql_port = config.mysql_port if port is None else port
        self.__mysql_db = config.mysql_db if db is None else db
        self.__username = config.mysql_username if user is None else user
        self.__password = config.mysql_password if password is None else password
        self.conn = None
        self.cur = None
        # 建立连接池，拒绝外部访问ip、端口等信息；
        try:
            self.conn = PooledDB(pymysql, maxcached=50, host=self.__mysql_ip, port=self.__mysql_port,
                                 user=self.__username,
                                 password=self.__password, db=self.__mysql_db).connection()
            if self.conn:
                self.cur = self.conn.cursor()
                print("Database: {} is connected successfully!".format(
                    self.__mysql_db))
            else:
                print("Database: {} is not connected, please try it again!".format(
                    self.__mysql_db))
                sys.exit(1)
        except Exception as e:
            print('Connection Error: ', e)

    def cursor(self):
        '''
        返回连接游标，可调用execute、fetch_all等
        '''
        return self.conn.cursor()

    def close(self):
        """
        主动关闭数据库连接
        """
        if self.conn:
            self.conn.close()
            print('Connection has been closed!')
        else:
            print('Error: can not close the connection which is None Type !')

    def execute_sql(self, sql=' '):
        """
        Base：执行sql语句，更新,删除等操作
        :param sql : sql语句
        """
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            error = 'MySQL execute failed! ERROR (%s): %s' % (
                e.args[0], e.args[1])
            print(error)
            log.error(error)
            return error

    def is_exist_table(self, table_name):
        """
        查看表是否已经存在
        :param table_name : table exists or not.
        """
        sql = "SELECT COUNT(*) From {}".format(table_name)
        result = self.execute_sql(sql)
        if result is None:
            return True
        else:
            if re.search("doesn't exist", result):
                return False
            else:
                return True

    def create_table(self, tablename, attrdict, constraint):
        """
        创建数据表
        :param tablename: eg,表名:'z_test_parekr'
        :param attrdict: eg, 属性键值对,{'name': 'varchar(30) NOT NULL'}
        :param constraint: eg, 主外键约束,"PRIMARY KEY(`id`)"
        Returns:
        """
        if self.is_exist_table(tablename):
            print('Error: can not create {} which exists in {}! '.format(
                tablename, self.__mysql_db))
            return
        sql = ''
        sql_mid = '`id` bigint(11) NOT NULL AUTO_INCREMENT,'
        for attr, value in attrdict.items():
            sql_mid = sql_mid + '`' + attr + '`' + ' ' + value + ','
        sql = sql + 'CREATE TABLE IF NOT EXISTS %s (' % tablename
        sql = sql + sql_mid
        sql = sql + constraint
        sql = sql + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'
        # ENGINE=InnoDB/MyISAM, InnoDB is recommended.
        print('creatTable:' + sql)
        self.execute_sql(sql)

    @property
    def get_version(self):
        """
        获取当前Mysql版本(方法属性化，语法糖)
        Returns:
        """
        self.cur.execute("SELECT VERSION()")
        return self.fetch_one_data()[0]

    # 获取查询的结果
    def fetch_one_data(self):
        """
        取得上个查询的单个结果
        """
        data = self.cur.fetchone()
        return data

    def insert_one(self, table_name, params):
        """插入一条记录
        :param table_name: 表名字
        :param params: 属性dict
        """
        key = []
        value = []
        for tmp_key, tmp_value in params.items():
            key.append(tmp_key)
            if isinstance(tmp_value, str):
                value.append("\'" + tmp_value + "\'")
            else:
                value.append(tmp_value)
        attrs_sql = '(' + ','.join(key) + ')'
        values_sql = ' values(' + ','.join(value) + ')'
        sql = 'insert into %s' % table_name
        sql = sql + attrs_sql + values_sql
        print('Insert One:' + sql)
        self.execute_sql(sql)

    def update_one(self, table_name: str, params: dict, conditions: dict):
        """
        更新一条记录:UPDATE 表名称 SET 列名称 = 新值 WHERE 列名称 = 某值
        :param table_name: 表名字
        :param params: 更新字段及数值
        :param conditions: 条件
        """
        update_sql = [k + '=' + "\'" +
                      str(v) + "\'" for k, v in params.items()]
        if conditions:
            conditions_sql = [k + '=' + "\'" +
                              str(v) + "\'" for k, v in conditions.items()]
            sql = 'update ' + table_name + ' set ' + \
                  ','.join(update_sql) + ' where ' + ','.join(conditions_sql)
        else:
            sql = 'update ' + table_name + ' set ' + ','.join(update_sql)
        print('Update One:', sql)
        self.execute_sql(sql)

    def insert_many(self, table: str, attrs: list, values: list):
        """插入多条数据
        :param table: 表名字, table='test_db'
        :param attrs: 属性键, key = ["id" ,"name", "age"]
        :param values: 属性值, value = [[101, "liuqiao", "25"], [102,"liuqiao1", "26"], [103 ,"liuqiao2", "27"], [104 ,"liuqiao3", "28"]]
        """
        values_sql = ['%s' for v in attrs]
        attrs_sql = '(' + ','.join(attrs) + ')'
        values_sql = ' values(' + ','.join(values_sql) + ')'
        sql = 'insert into %s' % table
        sql = sql + attrs_sql + values_sql
        print('insertMany:' + sql)
        try:
            for i in range(0, len(values), 20000):
                self.cur.executemany(sql, values[i:i + 20000])
                self.conn.commit()
        except pymysql.Error as e:
            self.conn.rollback()
            error = 'insertMany executemany failed! ERROR (%s): %s' % (
                e.args[0], e.args[1])
            print(error)

    def count_sql_query(self, sql_table, sql_condition=''):
        """
        统计表记录数
        :param sql_table: table_name
        :param sql_condition: condition limit
        """
        sql = "SELECT count(*) FROM " + sql_table + ' ' + sql_condition
        print(sql)
        self.cur.execute(sql)
        return list(self.cur.fetchall())[0][0]

    def sql_query(self, sql, df_header: list = None):
        """
        sql的查询，依据sql语句灵活查询，可返回dataframe。
        :param sql: sql语句
        :param df_header: dataframe的columns的名字列表
        :returns: sql查询结果
        """
        print(sql)
        self.cur.execute(sql)
        if not df_header:
            return self.cur.fetchall()
        else:
            result = self.cur.fetchall()
            df = pd.DataFrame(list(result), columns=df_header)
            return df

    def truncate_table(self, sql_table):
        """
        清空当前表
        """
        sql = "TRUNCATE table " + sql_table
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def delete_table(self, table, conditions=''):
        """
        删除当前表，符合条件内的数据
        :param table: table_name
        :param conditions: 筛选条件
        """
        sql = "DELETE FROM " + table + ' ' + conditions
        print("sql=", sql)
        self.cur.execute(sql)
        self.conn.commit()

    def drop_table(self, table, flag=False):
        """
        删库跑路（->__->）谨慎使用
        """
        if flag:
            sql = "DROP TABLE " + table
            print("Warning: " + sql)
            self.cur.execute(sql)
            self.conn.commit()


if __name__ == '__main__':
    Mysql_DB = MysqlUtils()
    print(Mysql_DB.get_version)

    # 创建表
    Mysql_DB.create_table('z_test_parekr', {
        'name': 'varchar(32) NOT NULL', "score": 'varchar(32)'
    }, "PRIMARY KEY(`id`)")

    # 插入一条记录
    # Mysql_DB.insert_one('z_test_parekr', {"name": "test", 'score': 'A+'})

    # 插入多条记录
    insert_value_list = [('parker', 'B'), ('andrew', 'C'), ('james', 'D')]
    Mysql_DB.insert_many('z_test_parekr', ['name', 'score'], insert_value_list)

    # 更新一条记录
    Mysql_DB.update_one('z_test_parekr', params={
        'name': 'parker'}, conditions={'id': 3})

    # 查询计数count
    # c = Mysql_DB.count_sql_query('z_test_parekr')
    # print(c)

    # 查询
    s = Mysql_DB.sql_query('SELECT * FROM z_test_parekr',
                           df_header=['id', 'name', 'score'])
    print(s)

    # 一次性清空数据表
    # Mysql_DB.truncate_table('z_test_parekr')

    # 删除清空数据表部分数据
    # Mysql_DB.delete_table('z_test_parekr', "WHERE name='andrew' ")

    Mysql_DB.drop_table('z_test_parekr', True)

    # 连接池，各操作提交和关闭。
    Mysql_DB.conn.commit()
    Mysql_DB.close()
