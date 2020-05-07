import json

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
