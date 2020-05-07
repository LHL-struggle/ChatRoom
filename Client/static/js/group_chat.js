var butt = document.getElementById("b");
var p1 = document.getElementById("p1");
var content = document.getElementById("content");

// 按钮点击事件
butt.onclick = function(){
    // 自己的用户名
    var addresser = $("#ycc").text()
    // 获取要发送的数据
    var message = content.value;
    // 添加用户自己所要发送的元素
    add_html = '<p style="text-align:right; margin-right:0;">' + addresser + ':' + message + '</p>';
    $("#p1").append(add_html);
    content.value = '';

    // 在点击发送时设置
    var height = p1.scrollHeight;       // 获取滚动页面高度
    //console.log(height);
    $("#p1").animate({scrollTop:height},'fast');     // jquery的animate方法，改变元素的高度，同时将垂直距离的位移距离设置为元素的高度

    $.ajax({
        type: "GET",
        contentType: "application/json; charset=UTF-8",
        dataType: "json",
        url: "/s_group_msg",
        data:{"message":message},
        timeout: 1000,
        success: function(data){
            //  接收返回结果，如果发送成功则返回1，发送失败返回0
            console.log(data["result"]);
        }
    });
};

//前端Ajax持续调用服务端，称为Ajax轮询技术
var getting = {
    url:'/r_group_msg',
    dataType:'json',
    success:function(res) {
    //console.log("成功返回了")
    console.log(res["message"]);
     // 要写入的HTML
    var add_html = '<p>' + res["addresser"] + ':' + res["message"] + '</p>';
    //写入数据
    $("#p1").append(add_html);

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