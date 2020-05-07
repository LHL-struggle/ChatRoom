# 导入前端框架flask
from flask import Flask, render_template, request, redirect, jsonify
# 导入套接字模块
import socket
# 导入json包
import json
import hanshu
import os
import threading
import time

LHL = Flask(__name__)

# 从客户段的配置文件client_conf.json中读取服务器的ip地址
ip_port_dict = json.load(open("client_conf.json", encoding="utf-8"))
# 1.创建流式套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 2.连接服务器
ip_port = (ip_port_dict["IP"], ip_port_dict["PORT"])
client_socket.connect(ip_port)

# 用于存放消息的字典
dict_chat = {1: [], 8: []}
# 其他接收的消息
qita_message = {}

# 接收消息
def R(client_socket):
    try:
        while 1:
            # 先接收消息大小
            data_len = int(hanshu.recv_msg(client_socket, 15).rstrip())
            # 接收内容
            recv_content = json.loads(hanshu.recv_msg(client_socket, data_len))
            if recv_content["type"] == 1:
                # 如果为私聊消息
                dict_chat[1].append(recv_content)
            if recv_content["type"] == 8:
                # 如果为群聊消息
                dict_chat[8].append(recv_content)
            if recv_content["type"] == 2:
                # 如果接收的为用户注册返回信息
                qita_message[2] = recv_content
            if recv_content["type"] == 3:
                # 校验用户名
                qita_message[3] = recv_content
            if recv_content["type"] == 4:
                # 登录信息
                qita_message[4] = recv_content
            if recv_content["type"] == 5:
                # 查看所有用户
                qita_message[5] = recv_content
            if recv_content["type"] == 6:
                # 添加好友请求
                qita_message[6] = recv_content
            if recv_content["type"] == 7:
                # 获取好友列表
                qita_message[7] = recv_content
            if recv_content["type"] == 9:
                # 如果接收的为用户删除好友服务端所返回的消息
                qita_message[9] = recv_content
            if recv_content["type"] == 10:
                # 如果接收的为用户保存个人信息服务端所返回的消息
                qita_message[10] = recv_content
            if recv_content["type"] == 11:
                # 如果接收的为用户提取个人信息服务端所返回的消息
                qita_message[11] = recv_content
    except:
        print("出错了")

threading.Thread(target=R, args=(client_socket,)).start()

'''
# 发送信息
def F(client_socket):
    send_dict = {"type": 1, "addresser": "吕浩亮", "recipients": "吕"}
    try:
        while 1:
            send_dict["message"] = input("吕浩亮:")
            hanshu.send_msg(client_socket, send_dict)
    except:
        print("断开连接")
        client_socket.close()

# 接收消息
def R(client_socket):
    try:
        while 1:
            # 先接收消息大小
            data_len = int(hanshu.recv_msg(client_socket, 15).rstrip())
            # 接收内容
            recv_content = json.loads(hanshu.recv_msg(client_socket, data_len))
            print("\r\n", recv_content['addresser'], ":", recv_content['message'])
    except:
        print("出错了")

threading.Thread(target=F, args=(client_socket,)).start()
threading.Thread(target=R, args=(client_socket,)).start()
'''

# 其他消息，从字典中获取信息
def qita_jieshu(type):
    # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
    recv_content = 0
    while recv_content == 0:
        recv_content = qita_message.get(type, 0)
    # 获取数据后，删除该键值对
    del qita_message[type]
    return recv_content

# 校验用户名与密码是否正确
def check(type):
    user_name = request.form.get("user_name")  # 获取用户名
    user_pwd = request.form.get("user_pwd")  # 获取用户密码
    content = {"user_name": user_name, "user_pwd": user_pwd}  # 将消息组成字典成为发送内容
    content_dict = {"type": type, "addresser": user_name, "recipients": "服务器", "message": content}
    hanshu.send_msg(client_socket, content_dict)  # 放送消息给服务器
    # 等待服务端消息

    # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
    recv_content = 0
    while recv_content == 0:
        recv_content = qita_message.get(type, 0)
    # 获取数据后，删除该键值对
    del qita_message[type]
    # 返回数据
    return recv_content

# 主界面
@LHL.route("/")
def home():
    addresser = None
    if os.path.exists("uname.json"):  # 判断文件是否存在
        addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 获取用户名
    is_login = request.cookies.get("is_login")
    return render_template("home.html", is_login=is_login, uname=addresser)

# 注册界面
@LHL.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":

        recv_content = check(2)
        #  如果服务器返回0 则代表注册成功
        if recv_content["message"] == 0:
            return render_template("login.html")  # 注册成功则进入登录界面
        else:
            return render_template("reg_fail.html")  # 注册失败则进入提醒页面

# 登录界面
@LHL.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        recv_content = check(4)             # 接收服务端的值
        if recv_content["message"] == 0:    # 0登录成功,1失败
            uname_dict = {"uname": request.form.get("user_name")}
            with open("uname.json", "wb") as f:
                f.write(json.dumps(uname_dict).encode())
            rsp = redirect("/")
            # 设置Cookie值，如果登录成功则Cookie值is_login = "LHL_struggle",max_age值为Cookie值有效时间
            rsp.set_cookie("is_login", "LHL_struggle",max_age=60*60)
            return rsp
        else:
            return render_template("login_fail.html")

# 校验用户名是否存在
@LHL.route("/check_uname")
def check_uname():
    user_name = request.args.get("user_name")
    content_dict = {"type": 3, "addresser": user_name, "recipients": "服务器", "message": user_name}
    hanshu.send_msg(client_socket, content_dict)  # 放送消息给服务器

    # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
    recv_content = 0
    while recv_content == 0:
        # recv_content 为接收到的信息
        recv_content = qita_message.get(3, 0)
    # 获取数据后，删除该键值对
    del qita_message[3]
    print(recv_content["message"])
    # 用户名存在返回1，不存在返回0
    return jsonify({"err": recv_content["message"]})    # 将字典转换为json格式返回

# 查看所有用户
@LHL.route("/Addfriends")
def Addfriends():
    if request.cookies.get("is_login") == "LHL_struggle":
        uname = json.load(open("uname.json", encoding="utf-8"))["uname"]
        send_dict = {"type": 5, "addresser": uname, "recipients": "服务器", "message": ""}
        hanshu.send_msg(client_socket, send_dict)  # 向服务器发出请求

        # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
        recv_content = 0
        while recv_content == 0:
            # recv_content 为接收到的信息
            recv_content = qita_message.get(5, 0)
        # 获取数据后，删除该键值对
        del qita_message[5]

        message = recv_content["message"]
        print(message)      # [['123123'], ['123456'], ['1234567'], ['159357'], ['456123']]
        return render_template("Addfriends.html", content=message)
    else:
        return render_template("/login")

# 添加好友请求
@LHL.route("/addf")
def addf():
    uname = json.load(open("uname.json", encoding="utf-8"))["uname"]   # 自己的用户名
    friend_name = request.args.get("uname")   # 得到对方用户名
    send_dict = {"type": 6, "addresser": uname, "recipients": "服务器", "message": friend_name}
    hanshu.send_msg(client_socket, send_dict)  # 发送消息

    # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
    recv_content = 0
    while recv_content == 0:
        # recv_content 为接收到的信息
        recv_content = qita_message.get(6, 0)
    # 获取数据后，删除该键值对
    del qita_message[6]

    return recv_content["message"]

# 获取好友列表
@LHL.route("/friends")
def friends():
    if request.cookies.get("is_login") == "LHL_struggle":
        uname = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
        send_dict = {"type": 7, "addresser": uname, "recipients": "服务器", "message": ""}
        hanshu.send_msg(client_socket, send_dict)  # 发送消息

        # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
        recv_content = 0
        while recv_content == 0:
            # recv_content 为接收到的信息
            recv_content = qita_message.get(7, 0)
        # 获取数据后，删除该键值对
        del qita_message[7]

        print(recv_content["message"])
        return render_template("friends.html", content=recv_content["message"])
    else:
        return render_template("/login")

# 删除好友
@LHL.route("/del_friend")
def del_friend():
    if request.cookies.get("is_login") == "LHL_struggle":
        uname = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
        FriendName = request.args.get("friend_name")   # 获取要删除的好友用户名
        del_FriendName = {"type": 9, "addresser": uname, "recipients": "服务器", "message": FriendName}   # 删除请求消息
        hanshu.send_msg(client_socket, del_FriendName)  # 发送消息

        # 接收删除好友请求，所返回的消息
        # 从存放信息的字典中，获取对应的信息，如果没有该信息，则值为0
        recv_content = 0
        while recv_content == 0:
            # recv_content 为接收到的信息
            recv_content = qita_message.get(9, 0)
        # 获取数据后，删除该键值对
        del qita_message[9]
        return recv_content["message"]
    else:
        return render_template("/login")

FriendName = ""
# 私聊聊天页面
@LHL.route("/friend_chat", methods=["POST", "GET"])
def friend_chat():
    if request.cookies.get("is_login") == "LHL_struggle":
        if request.method == "GET":
            addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
            global FriendName
            FriendName = request.args.get("uname")
            return render_template("friend_chat.html", uname=FriendName, addresser=addresser)
    else:
        return render_template("/login")

# 私聊发送消息
@LHL.route("/s_msg")
def s_msg():
    try:
        addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
        send_dict = {"type": 1, "addresser": addresser, "recipients": FriendName}
        send_dict["message"] = request.args.get("message")    # 获取要发送的内容
        hanshu.send_msg(client_socket, send_dict)   # 发送消息
        return jsonify({"result": 1})    # 发送成功返回1
    except:
        return jsonify({"result": 0})    # 发送失败返回0

# 聊天接收
def jieshu(type):
    try:
        recv_content = 0
        while recv_content == 0:
            time.sleep(0.5)
            # print(dict_chat)
            if len(dict_chat[type]) != 0:   # 如果私聊列表中有值存在
                # 删除并返回该元素
                recv_content = dict_chat[type].pop(0)

        print("你大爷", recv_content)
        return recv_content
    except:
        print("出错了")

# 聊天界面接收消息的
@LHL.route("/r_msg")
def r_msg():
    recv_content = jieshu(1)
    return jsonify(recv_content)

# 群聊页面
@LHL.route("/group_chat")
def group_chat():
    if request.cookies.get("is_login") == "LHL_struggle":
        addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
        return render_template("group_chat.html", addresser=addresser)
    else:
        return render_template("/login")

# 群聊发送
@LHL.route("/s_group_msg")
def s_group_msg():
    try:
        addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
        send_dict = {"type": 8, "addresser": addresser, "recipients": "all"}
        send_dict["message"] = request.args.get("message")    # 获取要发送的内容
        hanshu.send_msg(client_socket, send_dict)   # 发送消息
        return jsonify({"result": 1})    # 发送成功返回1
    except:
        return jsonify({"result": 0})    # 发送失败返回0

# 群聊接收
@LHL.route("/r_group_msg")
def r_group_msg():
    recv_content = jieshu(8)
    return jsonify(recv_content)

# 保存个人信息
@LHL.route("/save_message", methods=["POST", "GET"])
def save_message():
    if request.cookies.get("is_login") == "LHL_struggle":
        if request.method == "GET":
            addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
            return render_template("save_message.html", uname=addresser)
        if request.method == "POST":
            print("进入了post请求")
            addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 自己的用户名
            sign = request.form.get("sign")            # 获取表单中的签名(70)
            gender = request.form.get("gender")        # 获取性别(2)
            birthday = request.form.get("birthday")    # 获取生日（20）
            home = request.form.get("home")            # 所在地（50）
            school = request.form.get("school")        # 在读院校（40）
            professional = request.form.get("professional")  # 职业（40）
            elucidation = request.form.get("elucidation")    # 个人说明(150字)
            PerInfor = {"addresser": addresser, "sign": sign, "gender": gender, "birthday": birthday, "home": home, "school": school, "professional": professional, "elucidation": elucidation}
            send_dict = {"type": 10, "addresser": addresser, "recipients": "服务器", "message": PerInfor}
            print("获取到的数据%s" % PerInfor)
            hanshu.send_msg(client_socket, send_dict)     # 发送消息给服务端
            # 接收服务端的信息
            recv_content = qita_jieshu(10)    # 从字典中获取信息
            if recv_content["message"] == 1:   # 1表示保存成功，0代表未修改
                return "保存成功"
            else:
                return "保存失败"
    else:
        return render_template("/login")

# 个人信息显示页面
@LHL.route("/personal_show")
def personal_show():
    addresser = json.load(open("uname.json", encoding="utf-8"))["uname"]  # 获取用户名
    uname = request.args.get("uname")   # 获取需要查看用户的用户名
    send_dict = {"type": 11, "addresser": addresser, "recipients": "服务器", "message": uname}
    hanshu.send_msg(client_socket, send_dict)  # 发送消息给服务端
    # 接收服务端的信息
    recv_content = qita_jieshu(11)  # 从字典中获取信息
    if recv_content["message"]:    # 如果recv_content["message"]不为None
        # 所要查看个人信息的用户名加入到个人信息中
        recv_content["message"]["addresser"] = uname
        print(recv_content["message"])     # 打印出个人信息
        return render_template("personal_show.html", message=recv_content["message"])
    else:      # 如果为None
        PerInfor = {"addresser": uname, "sign": None, "gender": None, "birthday": None, "home": None, "school": None, "professional": None, "elucidation": None}
        return render_template("personal_show.html", message=PerInfor)

if __name__ == "__main__":
    LHL.run(port=80, debug=True)
