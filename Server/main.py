# 导入套接字模块
import socket
# 导入线程模块
import threading
# 导入json包
import json
from hanshu import send_msg, recv_msg, check_user_name, save_message,check_user_pwd, find_uname, save_per_infor, extract_per_infor
import os

# 读取json配置文件内容，并将它转换为字典
ip_port_dict = json.load(open("conf.json", encoding="utf-8"))
# 1.创建套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 2.绑定IP与端口号
Ip_Port = (ip_port_dict["IP"], ip_port_dict["PORT"])
server_socket.bind(Ip_Port)
# 3.将套接字设置为监听状态listen()
server_socket.listen(5)

client_socket_dict = {}  # 存用户名与客户端的套接字
uname_list = []  # 存在线用户名

# 测试聊天
'''
# 发送信息
def F(client_socket):
    send_dict = {"type": 1, "addresser": "服务器", "recipients": "吕浩亮"}
    try:
        while 1:
            send_dict["message"] = input("服务器:")
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
'''

add_fri = []  # 存放好友的列表
if not os.path.exists("friend.json"):     # 判断文件是否存在, 不存在则创建文件
    # friend.json 文件为好友集合文件
    with open("friend.json", "ab+") as f:   # 创建friend.json文件
        f.write(json.dumps({}).encode())

# 信息交互函数
def message(client_socket, client_address):
    # 与测试聊天对应
    '''
    # 发送信息线程
    threading.Thread(target=F, args=(client_socket,)).start()
    # 接收信息线程
    threading.Thread(target=R, args=(client_socket,)).start()
    '''
    try:
        while 1:
            # 先接收消息大小
            data_len = int(recv_msg(client_socket, 15).rstrip())
            # 接收内容，并转换为字典
            recv_content = json.loads(recv_msg(client_socket, data_len))
            print(recv_content)
            type = recv_content["type"]               # 消息类型
            addresser = recv_content["addresser"]     # 发送人
            recipients = recv_content["recipients"]   # 接收人
            message = recv_content["message"]         # 消息

            '''
            if not client_socket_dict.__contains__(addresser):  # 如果字典中没有这个键值对则
                client_socket_dict[addresser] = client_socket  # 在字典中加入键值对
                uname_list.append(addresser)  # 将用户名添加到在线用户列表中
            '''

            # 私聊请求
            if type == 1:
                # 检验对方是否在线
                if recipients in uname_list:
                    # 如果在线，则将此用户的信息发送给对方
                    to_socket = client_socket_dict[recipients]  # 收信人的套接字
                    send_msg(to_socket, recv_content)   # 发送消息给对方
                else:    # 如果不在线则不发消息给对方，并且回复发送者，对方不在线，请稍后在发送
                    recv_content["addresser"] = "服务器"
                    recv_content["recipients"] = addresser
                    recv_content["message"] = "对方不在线，请稍后在发送"
                    print(recv_content)   # 打印出消息
                    send_msg(client_socket, recv_content)
                    # print("发送成功")

            # 注册请求
            if type == 2:
                user_name = message["user_name"]   # 获取客户端发送过来的用户名
                user_pwd = message["user_pwd"]     # 获取客户端发送过来的密码
                recv_content["addresser"], recv_content["recipients"] = recipients, addresser
                if check_user_name(user_name) == 1:   # 用户名已存在
                    recv_content["message"] = 1
                if check_user_name(user_name) == 0:   # 用户名不存在
                    # 如果检验过后用户名不存在，则将用户名和用户密码存放到数据库中
                    if save_message(user_name, user_pwd):
                        recv_content["message"] = 0
                    else:
                        recv_content["message"] = 1
                print("要发送的数据：", recv_content)
                send_msg(client_socket, recv_content)   # 发送消息给客户端 0注册成功，1注册失败

            # 校验用户名
            if type == 3:
                recv_content["addresser"], recv_content["recipients"],  recv_content["message"] = recipients, addresser, check_user_name(message)
                print(recv_content["message"])
                send_msg(client_socket, recv_content)     #  发送消息给客户端 1存在，0不存在

            # 登录请求
            if type == 4:
                user_name = message["user_name"]  # 获取客户端发送过来的用户名
                user_pwd = message["user_pwd"]  # 获取客户端发送过来的密码
                # 将登录成功的用户，添加到在线列表中
                if check_user_pwd(user_name, user_pwd) == 0:
                    if not client_socket_dict.__contains__(addresser):  # 如果字典中没有这个键值对则
                        client_socket_dict[addresser] = client_socket  # 在字典中加入键值对
                        uname_list.append(addresser)  # 将用户名添加到在线用户列表中
                recv_content["addresser"], recv_content["recipients"], recv_content["message"] = recipients, addresser, check_user_pwd(user_name, user_pwd)
                send_msg(client_socket, recv_content)  #  发送消息给客户端 0登录成功，1登录失败

            # 查看用户请求
            if type == 5:
                recv_content["addresser"], recv_content["recipients"], recv_content["message"] = recipients, addresser, find_uname(addresser)
                print(recv_content["message"])
                send_msg(client_socket, recv_content)  # 响应客户端

            # 添加好友
            if type == 6:
                # friend.json文件为好友集合文件
                friends_dict = json.load(open("friend.json", encoding="utf-8"))
                if not friends_dict.__contains__(addresser):    # 判断文件中是否有关于这个用户的好友列表
                    # 如果没有添加这个用户的好友列表,就添加新的键值对，值由列表组成
                    friends_dict[addresser] = [message]
                    recv_content["message"] = "添加成功"
                else:   # 如果有则将新好友导入列表
                    if message in friends_dict[addresser]:
                        recv_content["message"] = "已为好友"
                    else:
                        friends_dict[addresser].append(message)
                        recv_content["message"] = "添加成功"
                with open("friend.json", "wb") as f:
                    f.write(json.dumps(friends_dict).encode())   # 将字典转换为字符串，再将字符串转换为字节型的写入friend.json中
                recv_content["addresser"], recv_content["recipients"] = recipients, addresser
                send_msg(client_socket, recv_content)  # 响应客户端

            # 获取好友列表
            if type == 7:
                friends_dict = json.load(open("friend.json", encoding="utf-8"))  # 读取json文件好友列表信息
                recv_content["addresser"], recv_content["recipients"] = recipients, addresser
                if not friends_dict.__contains__(addresser):     # 没有好友
                    recv_content["message"] = ["你还没有好友"]
                else:
                    recv_content["message"] = friends_dict[addresser]
                send_msg(client_socket, recv_content)  # 响应客户端

            # 删除好友请求
            if type == 9:
                friends_dict = json.load(open("friend.json", encoding="utf-8"))  # 读取存放好友列表的文件
                message = recv_content["message"]  # 消息
                recv_content["addresser"], recv_content["recipients"] = recipients, addresser
                if message in friends_dict[addresser]:   # 如果好友在列表中则删除好友
                    friends_dict[addresser].remove(message)   # 删除好友
                    with open("friend.json", "wb") as f:           # 打开文件
                        f.write(json.dumps(friends_dict).encode())   # 写入修改过的信息
                    recv_content["message"] = "删除成功"
                else:
                    recv_content["message"] = "没有该好友"
                send_msg(client_socket,recv_content)   # 响应客户端

            # 群聊请求
            if type == 8:
                # 遍历在线用户列表
                for x in uname_list:
                    if x != addresser:    # 发送消息给除开自己的用户
                        to_socket = client_socket_dict[x]  # 收信人的套接字
                        send_msg(to_socket, recv_content)  # 发送消息给对方

            # 保存个人信息
            if type == 10:
                # message  接收到的个人信息
                # save_per_infor(message)  1 表示保存或修改成功，0表是未修改
                recv_content["addresser"], recv_content["recipients"], recv_content["message"] = recipients, addresser, save_per_infor(message)
                send_msg(client_socket, recv_content)  # 响应客户端

            # 提取个人信息
            if type == 11:
                # message ，表示个人信息的用户名，并不一定是自己的，也有可能是好友的
                PerInfor = extract_per_infor(message)   # PerInfor 值为None或一个字典类型的数据
                recv_content["addresser"], recv_content["recipients"], recv_content["message"] = recipients, addresser, PerInfor
                send_msg(client_socket, recv_content)  # 响应客户端

    except:
        print("出错了")
        # 如果用户退出登录则，删除字典和列表中的值
        if client_socket_dict.__contains__(addresser):
            client_socket_dict.pop(addresser)  # 删除字典中的值
        if addresser in uname_list:
            uname_list.remove(addresser)
        client_socket.close()   # 关闭客户端套接字

# 主函数
def main():
    try:
        while 1:
            print("等待连接")
            # 等待客户端连接
            client_socket, client_address = server_socket.accept()
            print(client_socket, ":连接成功")
            # 创建信息交互线程，并启动
            threading.Thread(target=message, args=(client_socket, client_address,)).start()

    except:
        # 关闭服务器套接字
        server_socket.close()
        print("全部结束")

if __name__ == "__main__":
    main()






