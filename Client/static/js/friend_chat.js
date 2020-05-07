var butt = document.getElementById("b");
var p1 = document.getElementById("p1");
var content = document.getElementById("content");

// 按钮点击事件
butt.onclick = function(){
    var addresser = $("#yc").text()   // 获取自己的用户名
     console.log(addresser);
    var message = content.value;  // 获取要发送的数据
    // 添加在页面中添加元素并写入用户名及其内容
    add_html = '<p style="text-align:right; margin-right:0;">' +  addresser +':' + message + '</p>';
    $("#p1").append(add_html);
    content.value = '';  // 将输入框清空

    // 在点击发送时设置
    var height = p1.scrollHeight;       // 获取滚动页面高度
    //console.log(height);
    $("#p1").animate({scrollTop:height},'fast');     // jquery的animate方法，改变元素的高度，同时将垂直距离的位移距离设置为元素的高度


    // 利用ajax发送数据给客户端
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=UTF-8",
        dataType: "json",
        url: "/s_msg",
        data:{"message":message},
        timeout: 1000,
        success: function(data){
            console.log(data["result"]);  //  接收返回结果，如果发送成功则返回1，发送失败返回0
        }
    });
};

//前端Ajax持续调用服务端，称为Ajax轮询技术
var getting = {
    url:'/r_msg',    // 访问路径
    dataType:'json',
    success:function(res) {
    console.log(res["message"]);   // 在浏览器控制台，输出得到的聊天内容
    // 要写入的HTML res["addresser"]好友名， res["message"]好友发送的信息
    var add_html = '<p>' + res["addresser"] + ':' + res["message"] + '</p>';
    $("#p1").append(add_html); // 在显示框中写入数据

    // 在接收到消息时设置
    var height = p1.scrollHeight;       // 获取滚动页面高度
    //console.log(height);
    $("#p1").animate({scrollTop:height},'fast');     // jquery的animate方法，改变元素的高度，同时将垂直距离的位移距离设置为元素的高度


    //关键在这里，回调函数内再次请求Ajax
    $.ajax(getting);
    },
    //当请求时间过长（默认为60秒），就再次调用ajax长轮询
    error:function(res){ $.ajax(getting);}
};
$.ajax(getting);