import datetime

import pymysql
import time


def atoi(s):
    s = s[::-1]
    num = 0
    for i, v in enumerate(s):
        for j in range(0, 10):
            if v == str(j):
                num += j * (10 ** i)
    return num

def handleCarLeave(net_img_path, carnumber, platecolor, orgid):
    try:
        db = pymysql.connect(host='localhost',
                             database='travisparking',
                             user='root',
                             password='12345678',
                             port=3306)
    except:
        print("数据库连接失败！")
        return False
    else:
        # 创建一个游标对象  游标：可以执行sql语句，执行完sql语句有返回值
        cursor = db.cursor()  # 创建一个游标对象

        # 查询数据库中的现有车辆中是否含有当前车牌号
        sql_select = "select * from t_incar where t_incar.car_number=" + "\"" + carnumber + "\""  # 创建一条查询语句
        cursor.execute(sql_select)  # 执行sql语句
        all = cursor.fetchall()  # 用变量名all来接收游标返回的所有内容
        if len(all) == 0:
            return False  # 如果数据库中没有的话提示人工处理车辆离开

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        now2 = datetime.datetime.now()

        incar_color = all[0][2]
        incar_type = all[0][3]
        incar_judgecuser = all[0][4]
        incar_orgid = all[0][5]
        incar_entertime = all[0][6]
        incar_inurl = all[0][7]

        allSecondTime = (now2 - incar_entertime).seconds  # 时间间隔（秒）
        allMinuteTime = allSecondTime / 60   # 时间间隔（分钟）

        # 查询当前停车场对应的计费规则ID
        orgid = orgid[:orgid.find('_')]
        orgidint = atoi(orgid)
        sql_select2 = "select * from t_parklist where t_parklist.org_id=" + str(orgidint)  # 创建一条查询语句
        cursor.execute(sql_select2)  # 执行sql语句
        all2 = cursor.fetchall()  # 用变量名all来接收游标返回的所有内容
        if len(all2) == 0:
            return False  # 如果数据库中没有的话提示人工处理车辆离开
        priceId = all2[0][9]

        busyNumber = all2[0][3]
        busyNumber = int(busyNumber) - 1
        if busyNumber < 0:
            busyNumber = 0

        #busy停车位数量减一
        sql_update2 = "UPDATE t_parklist SET org_busynumber = " + str(busyNumber) + " WHERE t_parklist.org_id = " + str(orgidint)
        cursor.execute(sql_update2)  # 执行sql语句

        # 查询ID对应的计费规则
        sql_select3 = "select * from t_pricelist where t_pricelist.price_id=" + str(priceId)    # 创建一条查询语句
        cursor.execute(sql_select3)  # 执行sql语句
        all3 = cursor.fetchall()  # 用变量名all来接收游标返回的所有内容
        if len(all3) == 0:
            return False  # 如果数据库中没有的话提示人工处理车辆离开
        priceFreetime = all3[0][2]
        priceSecondtime = all3[0][3]
        priceSecondPrice = all3[0][4]
        priceOtherPrice = all3[0][5]
        priceMaxPrice = all3[0][6]

        if allMinuteTime <= priceFreetime:
            allCost = 0
        elif allMinuteTime <= (priceFreetime + priceSecondtime):
            allCost = (allMinuteTime - priceFreetime) * priceSecondPrice
        else:
            allCost = priceSecondtime * priceSecondPrice + (allMinuteTime - priceFreetime - priceSecondtime) * priceOtherPrice
            if allCost > priceMaxPrice:
                allCost = priceMaxPrice


        if incar_judgecuser == 1: # 属于常驻用户
            # 查询当前车牌号的用户是否为常驻用户
            sql_select4 = "select * from t_cuser where t_cuser.cuser_carnumber=" + "\"" + carnumber + "\""  # 创建一条查询语句
            cursor.execute(sql_select4)  # 执行sql语句
            all4 = cursor.fetchall()  # 用变量名all来接收游标返回的所有内容
            if len(all4) == 0:
                return False
            balance = all2[0][7]
            if allCost > balance:
                needPay = allCost - balance
                resultBalance = 0
            else:
                needPay = 0
                resultBalance = balance - allCost

            # 更新余额
            sql_update1 = "UPDATE t_cuser SET cuser_balance = " + str(resultBalance) + " WHERE cuser_carnumber = " + "\"" + carnumber + "\""
            cursor.execute(sql_update1)  # 执行sql语句
        else:
            needPay = allCost

        # 删除停车场中现有车辆的车辆信息
        sql_delete1 = "DELETE FROM t_incar WHERE t_incar.car_number = " + "\"" + carnumber + "\""
        cursor.execute(sql_delete1)  # 执行sql语句
        print("总计花费: " + str(allCost))
        print("需要支付: " + str(needPay))

        # 新增订单信息
        sql_insert = 'insert into t_orderlist(order_carnumber, order_carnumbercolor, order_cartype, order_judgecuser, order_orgid, order_entrytime, order_lefttime, order_cost, order_inurl, order_outurl, order_needpay) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'  # 创建一条插入语句
        values = [carnumber, platecolor, incar_type, incar_judgecuser, orgidint, incar_entertime, now, allCost, incar_inurl, net_img_path, needPay]
        cursor.execute(sql_insert, values)  # 执行sql语句
        db.commit()  # 确认 修改表内容后需要做确认操作

        db.close()
        cursor.close()
        return True


def handleAddCar(net_img_path, carnumber, platecolor, orgid):
    try:
        db = pymysql.connect(host='localhost',
                             database='travisparking',
                             user='root',
                             password='12345678',
                             port=3306)
    except:
        print("数据库连接失败！")
    else:
        # 创建一个游标对象  游标：可以执行sql语句，执行完sql语句有返回值
        cursor = db.cursor()  # 创建一个游标对象

        # 查询
        sql_select = "select * from t_cuser where t_cuser.cuser_carnumber=" + "\"" + carnumber + "\""  # 创建一条查询语句
        # print(sql_select)
        cursor.execute(sql_select)  # 执行sql语句
        all = cursor.fetchall()  #用变量名all来接收游标返回的所有内容
        judgecuser = 1
        if len(all) == 0:
            judgecuser = 0
        # print(all)

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        orgidint = atoi(orgid)
        cartype = "unknow"

        # busy停车位加一
        sql_select2 = "select * from t_parklist where t_parklist.org_id=" + str(orgidint)  # 创建一条查询语句
        cursor.execute(sql_select2)  # 执行sql语句
        all2 = cursor.fetchall()  # 用变量名all来接收游标返回的所有内容

        busyNumber = all2[0][3]
        busyNumber = int(busyNumber) + 1

        sql_update1 = "UPDATE t_parklist SET org_busynumber = " + str(busyNumber) + " WHERE t_parklist.org_id = " + str(orgidint)
        cursor.execute(sql_update1)  # 执行sql语句

        # 新增
        sql_insert = 'insert into t_incar(car_number, car_numbercolor, car_type, car_judgecuser, car_orgid, car_entertime, car_url) VALUES (%s,%s,%s,%s,%s,%s,%s)'  # 创建一条插入语句
        values = [carnumber, platecolor, cartype, judgecuser, orgidint, now, net_img_path]
        cursor.execute(sql_insert, values)  # 执行sql语句
        db.commit()  # 确认 修改表内容后需要做确认操作

        db.close()
        cursor.close()
