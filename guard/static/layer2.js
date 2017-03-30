
///////////////      case "protect_check":

function win_protect_check_private_func_gen_block(postion, status, postion_chs) {
    var icon = "icon_gate";
    switch (postion) {
        case "gate":
            icon = "icon_gate";
            break;
        case "kitchen":
            icon = "icon_kitchen";
            break;
        case "livingroom":
            icon = "icon_livingroom";
            break;
        case "window":
            icon = "icon_window";
            break;
    }
    str_html = "<!-- one li start -->	<li>"
    str_html += "<div class='protect_check_warnning_block'><img src='images/" + icon + ".png' /></div>"
    str_html += "<div ><span class='protect_check_WB_status' >" + status + "</span><span class='protect_check_WB_position'> <" + postion_chs + "> </span></div>"
    str_html += "</li> <!-- one li end --> "
    return str_html;
}
function win_protect_check_private_func_submit(type) {
    //time_stamp = Math.floor((new Date().getTime()) / 60000);
    $.ajax({
        url: "http://"+g_vars_domain_prefix+"/set_protect_start",
        data: {
            protect: type
        },
        type: 'get',
        cache: false,
        dataType: 'json',
        success: function(data) {
				console.warn("submit retrun:"+ JSON.stringify(data));
                //get_ui_state_fromServer();
        },
        error: function() {
			alert("网络连接异常！");
			//Popup_info_pop("网络连接异常！", "show", 1000);
        }
    });

}

var win_protect_check_devices_obj = new Object();
var win_protect_check_outcan_obj = new Object();

function win_protect_check_check_or_show(data) {
    //从json中保存window参数
    $.each(data["devices_status"], function(index, val) {
        //console.log("devices: ", index, val)
        if (val["status_code"] !== "0") {
            win_protect_check_devices_obj[index] = JSON.parse(JSON.stringify(val));
        }
    });
    win_protect_check_outcan_obj[0] = {
        "outgoing": "can"
    }
    win_protect_check_outcan_obj[1] = {
        "indoors": "can"
    }
    $.each(data["canprotect"], function(index, val) {
        //console.log("canprotect: " + index + JSON.stringify(val));
        win_protect_check_outcan_obj[index] = JSON.parse(JSON.stringify(val));

    });
	
	

	if (ui_state_current_shown == 'protect_check') {
		win_protect_check_init(); //将以上变量 赋值到相应的ui 控件上
		return 0;
	}
 

	//判断当前ui 是否是当前窗口，如果是设置 show shown事件 并返回1 。 如果不切换窗口则返回0
    $('#protect_check').on('show.bs.modal', function() {
        win_protect_check_init();
    });
    $('#protect_check').on('shown.bs.modal', function() {
        on_window_shown("protect_check");
    });
    return 1;
}

function win_protect_check_init() {
    //print input
    //console.log ( "in win_protect_check_init devices:",JSON.stringify(win_protect_check_devices_obj))
    //console.log ( "in win_protect_check_init canprotect:",JSON.stringify(win_protect_check_outcan_obj))
    str_html = ""
    var add_li_num = 0
    $.each(win_protect_check_devices_obj, function(index, val) {

        if ((val.status_code != '0') && (add_li_num < 6)) {
 
            if (debug_log_detail==1)console.log("protect_check  devices draw", val.type, val.status, val.position)
            str_html += win_protect_check_private_func_gen_block(val.type, val.status, val.position)
            // "type": "door",
            //"position": "户内门",
            //"status_code": "1",
            // "status": "未锁"
            add_li_num++;
        }
    });

    if (str_html == "") {
        str_html = "<li class='protect_check_WB_ok'>一切正常…… </li>"
        //document.getElementById("protect_check_btn_outgoing").disabled=""; 
        //document.getElementById("protect_check_btn_indoors").disabled="";
        if (debug_log_detail==1)console.log("protect_check set protect_check_btn_ both can")
		$('#protect_check_btn_outgoing').off('click');
        $('#protect_check_btn_outgoing').on('click', function() {
			audio_system_play_click();
            win_protect_check_private_func_submit("out")
        });
		$('#protect_check_btn_indoors').off('click');
        $('#protect_check_btn_indoors').on('click', function() {
			audio_system_play_click();
            win_protect_check_private_func_submit("home")
        });
    } else {
        //"0":{"out":"can"},"1":{"home":"can"}}
        $.each(win_protect_check_outcan_obj, function(index, val) {
            $.each(val, function(protect_mode, can_value) {
                if (debug_log_detail==1)console.log("protect_check set protect_check_btn_" + protect_mode, can_value)
                if (can_value == 'cannot') {
					$('#protect_check_btn_' + protect_mode).off('click');
                    $('#protect_check_btn_' + protect_mode).on('click', function() {
						audio_system_play_error();
                        Popup_info_pop("不能进行设备设防状态，请检查设备情况。", "show", 1000);
                    });
                } else{
					$('#protect_check_btn_' + protect_mode).off('click');
                    $('#protect_check_btn_' + protect_mode).on('click', function() {
						audio_system_play_click();
                        win_protect_check_private_func_submit(protect_mode)
                    });
				}
            });
        });

    }
    $('#protect_check_ul').html(str_html)
    //console.log ( "in win_protect_check_init" ,$('#protect_check_ul').html() );

}
function win_protect_check_stop() {
	$('#protect_check_btn_outgoing').off('click');
	$('#protect_check_btn_indoors').off('click');
}
 
		  




///////////////      case "protect_starting":
var win_protect_starting_inittime;
var win_protect_starting_init_time_remained;
var win_protect_starting_timer;
var win_protect_starting_protectmode;
var win_protect_starting_static_isclose=1;
function win_protect_starting_submit(type) {
    
	//win_protect_starting_stop() ;
    $.ajax({
        url: "http://"+g_vars_domain_prefix+ "/set_protect",
        data: {
            mode: win_protect_starting_protectmode,
            result: type
        },
        type: 'get',
        cache: false,
		async: false,
        dataType: 'json',
        success: function(data) {
            	console.warn("submit retrun:"+ JSON.stringify(data));
                //get_ui_state_fromServer();
        },
        error: function() {
			alert("网络连接异常！");
        }
    });
	
}

function win_protect_starting_timer_event() {
	if (win_protect_starting_static_isclose == 1) return;

    now_time = (new Date().getTime()) / 1000
    total_remain = Math.floor(win_protect_starting_init_time_remained - (now_time - win_protect_starting_inittime))
    if (debug_log_detail==1)console.log("in win_protect_starting_timer_event", total_remain);
    $('#protect_starting_timeremain').html( "<font>"+total_remain+"</font>");

    if (total_remain > 0  ) {
        win_protect_starting_timer = window.setTimeout(function() {
            win_protect_starting_timer_event();
        }, 500);
    } else{
        win_protect_starting_submit("ok");
	}


}

function win_protect_starting_check_or_show(data) {
    ////分析 wininit 的参数 status': 'protect_starting', 'protect_mode': 'out', 'timer_remain': 59

    win_protect_starting_inittime = (new Date().getTime()) / 1000;
    win_protect_starting_init_time_remained = data.remain_second;

    win_protect_starting_protectmode = data.house_status;

	
	if (ui_state_current_shown == 'protect_starting'){
		win_protect_starting_init("part_ui");
		return 0;
	}
	$('#protect_starting').on('show.bs.modal', function() {
		$('#protect_starting_status').html();
		$('#protect_starting_timeremain').html();
    });

    $('#protect_starting').on('shown.bs.modal', function() {
		win_protect_starting_static_isclose = 0;
        win_protect_starting_init("all_ui");
		on_window_shown('protect_starting');
    });
    return 1;

}

function win_protect_starting_init(ispart) {
	switch (win_protect_starting_protectmode)
	{
		case "outgoing":
				str_protectmode = "外出";
			break
		case "indoors":
				str_protectmode = "居家";
			break
		default:
				str_protectmode = "未知";
	}
    $('#protect_starting_status').html("即将进入" + str_protectmode + "保护模式");


	$('#protect_starting_btn-cancel').off('click');
	$('#protect_starting_btn-cancel').on('click', function() {
		audio_system_play_click();
        win_protect_starting_submit("cancel")
    });

	if (ispart=="all_ui")
	{
		$('#protect_starting_timeremain').html("<font>"+win_protect_starting_init_time_remained+"</font>" );
		audio_system_play_time_warning();
		win_protect_starting_inittime = (new Date().getTime()) / 1000;
		win_protect_starting_timer = window.setTimeout(function() {
			win_protect_starting_timer_event();
		}, 500);
	}


}
function win_protect_starting_stop() {
	win_protect_starting_static_isclose = 1;

    $('#protect_starting_btn-cancel').off('click');
    audio_system_stop_all();
	window.clearTimeout(win_protect_starting_timer);


}





///////////////      case "protected":
var win_protected_protectmode;


function win_protected_check_or_show(data) {
    ////分析 wininit 的参数'status': 'protected', 'protect_mode': 'out'
	win_protected_protectmode = data.house_status;

	if (ui_state_current_shown == 'protected'){
		win_protected_init(); //for update
		return 0;
	}
    $('#' + data.status).on('shown.bs.modal', function() {
		$('#protected_btn-cancel').on('click', function() {
			audio_system_play_click();
			win_unlock_protect_submit("start", "");
		});
        on_window_shown('protected');
    });

    $('#' + data.status).on('show.bs.modal', function() {
        win_protected_init();
    });
	 
    return 1;
}
function win_protected_init() {
		switch (win_protected_protectmode)
	{
		case "outgoing":
				str_protectmode = "外出";
			break
		case "indoors":
				str_protectmode = "居家";
			break
		default:
				str_protectmode = "未知";
	}

    $('#protected_status').html("已设防，" + str_protectmode + "模式 ");

}

function win_protected_stop() {
    $('#protected_status').html();
    $('#protected_btn-cancel').off('click');
}





///////////////      case "unlock_protect":
var win_unlock_protect_protectmode;
var win_unlock_protect_remain_seconds;
var win_unlock_protect_timer;
var win_unlock_protect_inittime;
var win_unlock_protect_is_colsed=1;
function win_unlock_protect_submit(okorcancel, passwd) {
    
	time_stamp = Math.floor((new Date().getTime()) / 60000);
	time_stamp= String(time_stamp);
	passwd= passwd + time_stamp;
	console.log(passwd);
	passwd=hex_md5(passwd).toLowerCase()
    $.ajax({
        url: "http://"+g_vars_domain_prefix+"/set_cancel_protected",
        data: {
            mode: win_protected_protectmode,
            action: okorcancel,
			systime:time_stamp,
            passwd: passwd
        },
        type: 'get',
        cache: false,
        dataType: 'json',
        success: function(data) {
            	console.warn("submit retrun:"+ JSON.stringify(data));
                //get_ui_state_fromServer();		
        },
        error: function() {

            alert("网络连接异常！");
        }
    });

}

function win_unlock_protect_timer_event() {
	if (win_unlock_protect_is_colsed == 1)
	{
		return;
	}
    now_time = (new Date().getTime()) / 1000
    total_remain = Math.floor(win_unlock_protect_remain_seconds - (now_time - win_unlock_protect_inittime))
    console.log("in win_unlock_protect ", total_remain);
    $('#unlock_protect_remain_seconds').html(total_remain);
    if (win_unlock_protect_is_colsed==0 && total_remain > 0) {
        win_unlock_protect_timer = window.setTimeout(function() {
            win_unlock_protect_timer_event();
        }, 500);
    } else if (win_unlock_protect_is_colsed == 0)	{
		console.error(" win_unlock_protect_submit cancel", total_remain);
        win_unlock_protect_submit("cancel", "");
	}
}

function win_unlock_protect_check_or_show(data) {
    //分析 wininit 的参数'status': 'unlock_protect', 'timer_remain': 60,
    win_unlock_protect_protectmode = data.protect_mode;
    win_unlock_protect_remain_seconds = data.remain_second;
	//console.error("unlock_protect timer remained  init value is " + data.remain_second)
	$('#unlock_protect_remain_seconds').html(win_unlock_protect_remain_seconds);

	win_unlock_protect_is_colsed=0;
	if (ui_state_current_shown == 'unlock_protect') {
		return 0;
	}
	 $('#' + data.status).on('show.bs.modal', function() {
			$('#unlock_protect_remain_seconds').html();
	 });
     $('#' + data.status).on('shown.bs.modal', function() {
		win_unlock_protect_is_colsed =0;
		win_unlock_protect_inittime = (new Date().getTime()) / 1000;
        win_unlock_protect_timer = window.setTimeout(function() {
            win_unlock_protect_timer_event();
        }, 500);

        virual_password_keyboard_init("win_unlock_protect_input", function(pw) {
			win_unlock_protect_stop();
            win_unlock_protect_submit("ok", pw);
			
        });

		on_window_shown('unlock_protect');

    });


    return 1;
}
function win_unlock_protect_stop() {
		
		win_unlock_protect_is_colsed =1;
		window.clearTimeout(win_unlock_protect_timer);
		
		virual_password_keyboard_close(); 
}






///////////////      case "alert_message":
var win_alert_message_protectmode;
var win_alert_message_explain;
var win_alert_message_alertid;

function win_alert_message_submit(alertid) {
    //time_stamp = Math.floor((new Date().getTime()) / 60000);

    $.ajax({
        url: "http://"+g_vars_domain_prefix+"/stop_alert",
        data: {
            alertid: alertid,
        },
        type: 'get',
        cache: false,
        dataType: 'json',
        success: function(data) {
            	console.warn("submit retrun:"+ JSON.stringify(data));
                //get_ui_state_fromServer();	            	
        },
        error: function() {
            alert("网络连接异常！");
        }
    });
}

function win_alert_message_init() {
	$('#alert_message_explain').html(win_alert_message_explain);
}

function win_alert_message_check_or_show(data) {
    //分析 wininit 的参数 
    win_alert_message_protectmode = data.house_status;
    //win_alert_message_alertid ="343wsrwws"
    //win_alert_message_explain ="厨房检测到火警 "
    var first_found = 0;
    $.each(data["devices_status"], function(index, val) {
        if ((val.status_code != '0') && (first_found == 0)) {
            //console.log ( "alert_message   draw", JSON.stringify(val))
            if (debug_log_detail==1)console.log("alert_message   draw", val.uuid, val.position, val.status, val.alert_detail)
            win_alert_message_alertid = val.uuid;
            if ((typeof(val.alert_detail) == "undefined") || (val.alert_detail == "")) {
                win_alert_message_explain = val.position + val.status;
            } else
                win_alert_message_explain = val.alert_detail;

            first_found = 1;
        }

    });


	if (ui_state_current_shown == 'alert_message'){
		win_alert_message_init();
		return 0;
	}

    $('#' + data.status).on('shown.bs.modal', function() {

		$('#alert_message_btn-stopalert').on('click', function() {
			audio_system_play_click();
            win_alert_message_submit(win_alert_message_alertid);
        });
		audio_system_play_alerm();
        on_window_shown('alert_message');
    });

    $('#' + data.status).on('show.bs.modal', function() {
		win_alert_message_init();
    });

    return 1;
}
function win_alert_message_stop() {
	audio_system_stop_all();
    $('#alert_message_btn-stopalert').off('click');
	
}

///////////////      case "bell_ring":
var win_bell_ring_bellid;
var win_bell_ring_description;
var win_bell_ring_jsoncache;
function win_bell_ring_submit(bellid, action) {
    //time_stamp = Math.floor((new Date().getTime()) / 60000);
    $.ajax({
        url: "http://"+g_vars_domain_prefix+"/bell_do",
        data: {
            bellid: bellid,
            action: action,
        },
        type: 'get',
        cache: false,
        dataType: 'json',
        success: function(data) {
            	console.warn("submit retrun:"+ JSON.stringify(data));
                //get_ui_state_fromServer();	
        },
        error: function() {
            alert("网络连接异常！");
        }
    });
}

function win_bell_ring_init() {
	$('#bell_ring_description').html(win_bell_ring_description + "呼叫……");



}


function win_bell_ring_check_or_show(data) {
    //分析 wininit  
	if ( data.bell_status == "ringing")
	{
			$.each(data["devices_status"], function(index, val) {

				if (val.type == "doorbutton" && val.status_code != 0)
				{
					console.log( val.type ,val.status_code ,val.status , val.video_url ,val.position, val.uuid);
					win_bell_ring_jsoncache = JSON.parse(JSON.stringify(val));

				}
        });
	}

	win_bell_ring_bellid = win_bell_ring_jsoncache.uuid;
	win_bell_ring_description = win_bell_ring_jsoncache.position;
   

    
	if (ui_state_current_shown == 'bell_ring'){
		win_bell_ring_init();
		return 0;
	}
    $('#' + data.status).on('shown.bs.modal', function() {

		$('#bell_ring_startstream').on('click', function() {
			audio_system_play_click();
			win_bell_ring_submit(win_bell_ring_bellid, "startstream");
		});
		$('#bell_ring_opendoor').on('click', function() {
			audio_system_play_click();
			win_bell_ring_submit(win_bell_ring_bellid, "opendoor");
		});
		$('#bell_ring_reject').on('click', function() {
			audio_system_play_click();
			win_bell_ring_submit(win_bell_ring_bellid, "reject");
		});

		audio_system_play_bell_ring();
        on_window_shown('bell_ring');
    });
	$('#' + data.status).on('show.bs.modal', function() {
		win_bell_ring_init();
	});
    return 1;
}
function win_bell_ring_stop() {
	audio_system_stop_all();
	$('#bell_ring_startstream').off('click');
	$('#bell_ring_opendoor').off('click');
	$('#bell_ring_reject').off('click');

}


///////////////      case "bell_view":
var win_bell_view_bellid;
var win_bell_view_video_url;
var win_bell_view_description;
var win_bell_view_jsoncache;

function myBrowser(){
    var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
    var isOpera = userAgent.indexOf("Opera") > -1;
    if (isOpera) {
        return "Opera"
    }; //判断是否Opera浏览器
    if (userAgent.indexOf("Firefox") > -1) {
        return "Firefox";
    } //判断是否Firefox浏览器
    if (userAgent.indexOf("Chrome") > -1){
  return "Chrome";
 }
    if (userAgent.indexOf("Safari") > -1) {
        return "Safari";
    } //判断是否Safari浏览器
    if (userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera) {
        return "IE";
    }; //判断是否IE浏览器
}
function win_bell_view_init() {

	$('#bell_view_description').html(win_bell_view_description + "视频中……");
	
 	if (win_bell_view_video_url != "") {
		var htmlvideo_control =  document.getElementById("bell_view_video");
		if (htmlvideo_control != null)
		{
			//console.log(JSON.stringify(htmlvideo_control));
			htmlvideo_control.src = win_bell_view_video_url;
			//htmlvideo_control.play();
		}
 
		if (  myBrowser() == "Firefox")
		{
			    doGo(win_bell_view_video_url);
		} 
		 
		
	}
    
}
function win_bell_view_check_or_show(data) {
    //分析 wininit  
	if ( data.bell_status == "conversation")
	{
			$.each(data["devices_status"], function(index, val) {

				if (val.type == "doorbutton" && val.status_code != 0)
				{
					console.log( val.type ,val.status_code ,val.status , val.video_url ,val.position, val.uuid);
					win_bell_view_jsoncache = JSON.parse(JSON.stringify(val));

				}
        });
	}
    win_bell_view_bellid = win_bell_view_jsoncache.uuid;
	win_bell_view_description = win_bell_view_jsoncache.position;
    win_bell_view_video_url = win_bell_view_jsoncache.video_url;

	 
	
	if (ui_state_current_shown == 'bell_view'){
		win_bell_view_init();
		return 0;
	}
	$('#' + data.status).on('shown.bs.modal', function() {
		$('#bell_view_opendoor').on('click', function() {
			audio_system_play_click();
			win_bell_ring_submit(win_bell_view_bellid, "opendoor");
		});
		$('#bell_view_reject').on('click', function() {
			audio_system_play_click();
			win_bell_ring_submit(win_bell_view_bellid, "reject");
		});
		
		
        on_window_shown('bell_view');
    });
	$('#' + data.status).on('show.bs.modal', function() {
		win_bell_view_init();
	});
    return 1;
}
function win_bell_view_stop() {
	//audio_system_stop_all();
	$('#bell_view_opendoor').off('click');
	$('#bell_view_reject').off('click');

	var htmlvideo_control =  document.getElementById("bell_view_video");
	if (htmlvideo_control != null)
	{
		
		htmlvideo_control.pause();
		htmlvideo_control.src="";
	}
	if ( myBrowser() == "Firefox")
	{
		document.getElementById("layer1_cover_vlc").style.opacity="1";
		doStop();
			
	} 
  
 


}



/*
		var timer1;
		var last_ui_stats = ""
		function test () {


				window.clearTimeout(timer1);

				//alert(last_ui_stats);
					
				 if (last_ui_stats=="")
				 {
					last_ui_stats="protect_check"
					$('#'+last_ui_stats).modal("show")

				 }else if (last_ui_stats=="protect_check")
				 {
					
					$('#'+last_ui_stats).modal("hide")
					
					$('#'+last_ui_stats).on('hidden.bs.modal', function() {
						last_ui_stats="protect_starting"
						$('#'+last_ui_stats).modal("show");
					});
					
					
				 }else if (last_ui_stats=="protect_starting")
				 {
					var temp_state = last_ui_stats
					
					last_ui_stats="protected"
					$('#'+last_ui_stats).modal("show")
					$('#'+last_ui_stats).on('shown.bs.modal', function() {
						$('#'+temp_state).modal("hide")
					});
					
				 }else if (last_ui_stats=="protected")
				 {
					
					$('#'+last_ui_stats).modal("hide")
					last_ui_stats="unlock_protect"
					$('#'+last_ui_stats).modal("show")
				 }else if (last_ui_stats=="unlock_protect")
				 {
					
					$('#'+last_ui_stats).modal("hide")
					last_ui_stats="alert_message"
					$('#'+last_ui_stats).modal("show")
				 }else if (last_ui_stats=="alert_message")
				 {
					
					$('#'+last_ui_stats).modal("hide")
					last_ui_stats="bell_ring"
					$('#'+last_ui_stats).modal("show")
				 }else if (last_ui_stats=="bell_ring")
				 {
					
					$('#'+last_ui_stats).modal("hide")
					last_ui_stats="bell_view"
					$('#'+last_ui_stats).modal("show")
				 }else if (last_ui_stats=="bell_view")
				 {
					
					$('#'+last_ui_stats).modal("hide")
					last_ui_stats=""

				 }
			


				//try { throw new Error("dummy"); } catch (e) { console.log(e.stack); }
				//$('#'+last_ui_stats).on('shown.bs.modal', function() {
						timer1 = window.setTimeout (function () {
							test();
						},5000);
					//});	 
				 
				
		  }
*/