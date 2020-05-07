import json
import pymysql

# 读取db.json文件内容，并将他转换为字符串
db_message = json.load(open("db.json", encoding="utf8"))

# 发送消息的函数
def send_msg(client_socket, data):
    '''
    :param client_socket: 客户端套接字
    :param data:  需要发送的信息，data是字典型数据
    :return: 无返回值
    '''
    # print(data)
    # 将字典转换为字符串,在将他转换为字节型
    data_bytes = json.dumps(data).encode()
    # 求取消息大小在将他转换为字符型，填充到15宽度，转换为字节型
    data_len = str(len(json.dumps(data))).ljust(15).encode()
    # 发送消息大小
    client_socket.send(data_len)
    # 发送消息内容
    client_socket.send(data_bytes)

# 接收消息函数
def recv_msg(client_socket, data_len):
    '''
    :param client_socket: 客户端套接字
    :param data_len: data_len 接收数据的大小
    :return: data_str 消息类型为字符串
    '''
    # 实际接收信息的大小
    recv_size = 0
    # 接收信息的内容
    data_str = ''
    # 如果接收信息的实际大小，小于或等于应接收数据大小，那么将一直循环接收
    while recv_size <= data_len:
        # 单次接收信息的内容,并转换为字符串
        recv_content = client_socket.recv(data_len - recv_size).decode()
        # 如果接收内容为空，则跳出循环
        if not recv_content:
            break
        # 累计接收的信息大小
        recv_size += len(recv_content)
        # 累计接收的内容
        data_str += recv_content
    return data_str

# 校验用户名
def check_user_name(user_name):
    # 连接数据库，db_conn为Connection对象
    conn = pymysql.connect(db_message["db_server"], db_message["db_user"], db_message["db_password"], db_message["db_name"])
    try:
        with conn.cursor() as cur:    # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的sql语句
            cur.execute("select uname from user where uname=%s", (user_name,))
            # 通过游标获取执行结果获取单条结果
            rows = cur.fetchone()
    finally:   # 无论try语句中有无出错.最后都要关闭数据库连接
        conn.close()
    if rows:
        # 用户名存在
        return 1
    return 0

# 将用户信息存放到数据库中
def save_message(user_name,user_pwd):
    # 连接数据库，db_conn为Connection对象
    conn = pymysql.connect(db_message["db_server"], db_message["db_user"], db_message["db_password"], db_message["db_name"])
    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的sql语句
            cur.execute("insert into user (uname, upass) values (%s,password(%s))", (user_name, user_pwd))
            row = cur.rowcount  # 执行语句所影响的行数
            print("影响行数：%s" % row)
            conn.commit()     # 提交到数据库
    except:
        conn.rollback()   # 如果发生错误则回滚
    finally:  # 无论try语句中有无出错.最后都要关闭数据库连接
        conn.close()
    return row


# 校验用户名
def check_user_pwd(user_name, user_pwd):
    # 连接数据库，db_conn为Connection对象
    conn = pymysql.connect(db_message["db_server"], db_message["db_user"], db_message["db_password"], db_message["db_name"])
    try:
        with conn.cursor() as cur:    # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的sql语句
            cur.execute("select * from user where uname=%s and upass=password(%s)", (user_name, user_pwd))
            # 通过游标获取执行结果获取单条结果
            rows = cur.fetchone()
            print(rows)
    finally:   # 无论try语句中有无出错.最后都要关闭数据库连接
        conn.close()
    if rows:
        # 用户名存在
        return 0
    return 1

# 查看所有用户
def find_uname(addresser):
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(db_message["db_server"], db_message["db_user"], db_message["db_password"], db_message["db_name"])
    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from user where uname != %s ", (addresser,))
            # 通过游标获取执行结果
            rows = cur.fetchall()
    finally:
        # 关闭数据库连接
        conn.close()
    return rows


# 将个人信息保存到数据库
def save_per_infor(message):
    '''
    :param message: 为一个字典类型的数据{"addresser": addresser, "sign": sign, "gender": gender, "birthday": birthday,
    "home": home, "school": school, "professional": professional, "elucidation": elucidation}
    :return hang:  0保存或修改失败，1保存成功
    '''

    # 连接数据库，db_conn为Connection对象
    conn = pymysql.connect(db_message["db_server"], db_message["db_user"], db_message["db_password"], db_message["db_name"])
    # 影响的行数
    hang = 0    # 默认影响行数
    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 查询InforTable表中是否存有个人信息
            cur.execute("select PerInfor from InforTable where uname = %s", (message["addresser"],))
            # 通过游标获取执行结果获取单条结果
            row = cur.fetchone()
            if row:    # 如果存有这个人的信息
                old_message = json.loads(row[0])       # 将字符串转换为字典,未改变的信息
                if len(message["sign"]) != 0:          # 如果签名不为空，则替换掉old的签名
                    old_message["sign"] = message["sign"]
                if len(message["gender"]) != 0:        # 如果性别不为空，则替换old性别
                    old_message["gender"] = message["gender"]
                if len(message["birthday"]) != 0:      # 如果生日日期不为空，则替换old生日日期
                    old_message["birthday"] = message["birthday"]
                if len(message["home"]) != 0:          # 所在地址
                    old_message["home"] = message["home"]
                if len(message["school"]) != 0:        # 所读院校
                    old_message["school"] = message["school"]
                if len(message["professional"]) != 0:  # 从事职业
                    old_message["professional"] = message["professional"]
                if len(message["elucidation"]) != 0:   # 个人说明
                    old_message["elucidation"] = message["elucidation"]
                # 将字典转换为字符串
                new_message = json.dumps(old_message)
                try:
                    # 修改数据信息
                    cur.execute("UPDATE InforTable SET PerInfor = %s WHERE uname = %s", (new_message, message["addresser"]))
                    # 执行语句所影响的行数
                    hang = cur.rowcount
                    print("影响行数：%s" % hang)
                    conn.commit()  # 提交到数据库
                except:
                    conn.rollback()  # 如果发生错误则回滚
            else:      # 如果数据库中没有存这个用户的个人信息
                try:
                    # 插入数据
                    new_message = {"sign": message["sign"], "gender": message["gender"], "birthday": message["birthday"], "home": message["home"], "school": message["school"], "professional": message["professional"], "elucidation": message["elucidation"]}
                    new_message = json.dumps(new_message)    # 将字典转换为字符串
                    # 插入数据库
                    cur.execute("insert into InforTable (uname, PerInfor) values (%s,%s)", (message["addresser"], new_message))
                    # 执行语句所影响的行数
                    hang = cur.rowcount
                    print("影响行数：%s" % hang)
                    conn.commit()  # 提交到数据库
                except:
                    conn.rollback()  # 如果发生错误则回滚
    finally:  # 无论try语句中有无出错.最后都要关闭数据库连接
        conn.close()
    return hang       # 如果影响行数不为0，则表示保存成功

# 提取某个人的个人信息
def extract_per_infor(uname):
    '''
    :param uname: 所要查看信息的用户名
    :return PerInfor: 返回的个人信息，要不就是None,要不就是一个字典型的个人信息
    '''
    # 连接数据库
    conn = pymysql.connect(db_message["db_server"], db_message["db_user"], db_message["db_password"], db_message["db_name"])
    try:
        with conn.cursor() as cur:    # 创建游标
            # 查询InforTable表中是否存有个人信息
            cur.execute("select PerInfor from InforTable where uname = %s", (uname,))
            # 通过游标获取执行结果获取单条结果
            row = cur.fetchone()     # 当没有此用户信息时则 row=None,有信息则row=("PerInfor",)
            if row:
                PerInfor = json.loads(row[0])   # 将字符串转换为字典
            else:
                PerInfor = row
    finally:
        conn.close()   # 关闭数据库连接
    return PerInfor
