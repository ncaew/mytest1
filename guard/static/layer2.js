
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
	//将以上变量 赋值到相应的ui 控件上
	win_protect_check_init();

	if (ui_state_current_shown == 'protect_check') return 0;
 

	//判断当前ui 是否是当前窗口，如果是设置 show shown事件 并返回1 。 如果不切换窗口则返回0
    $('#protect_check').on('show.bs.modal', function() {
        
    });
    $('#protect_check').on('shown.bs.modal', function() {
        system_close_last_window("protect_check");
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
        $('#protect_check_btn_outgoing').on('click', function() {
			audio_system_play_click();
            win_protect_check_private_func_submit("out")
        });
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
                    $('#protect_check_btn_' + protect_mode).on('click', function() {
						audio_system_play_error();
                        Popup_info_pop("不能进行设备设防状态，请检查设备情况。", "show", 1000);
                    });
                } else
                    $('#protect_check_btn_' + protect_mode).on('click', function() {
						audio_system_play_click();
                        win_protect_check_private_func_submit(protect_mode)
                    });
            });
        });

    }
    $('#protect_check_ul').html(str_html)
    //console.log ( "in win_protect_check_init" ,$('#protect_check_ul').html() );

}
function win_protect_check_stop() {
	//关闭声音
	audio_system_stop_all();

	$('#protect_check_btn_outgoing').off('click');
	$('#protect_check_btn_indoors').off('click');
}
 
		  




///////////////      case "protect_starting":
var win_protect_starting_inittime;
var win_protect_starting_init_time_remained;
var win_protect_starting_timer;
var win_protect_starting_protectmode;

function win_protect_starting_submit(type) {
    //time_stamp = Math.floor((new Date().getTime()) / 60000);
	
    $.ajax({
        url: "http://"+g_vars_domain_prefix+ "/set_protect",
        data: {
            mode: win_protect_starting_protectmode,
            result: type
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

function win_protect_starting_timer_event() {
    now_time = (new Date().getTime()) / 1000
    total_remain = Math.floor(win_protect_starting_init_time_remained - (now_time - win_protect_starting_inittime))
    if (debug_log_detail==1)console.log("in win_protect_starting_timer_event", total_remain);
    $('#protect_starting_timeremain').html( "<font face='兰亭黑' >"+total_remain+"</font>");
    if (total_remain > 0) {
        win_protect_starting_timer = window.setTimeout(function() {
            win_protect_starting_timer_event();
        }, 1000);
    } else
        win_protect_starting_submit("ok");


}

function win_protect_starting_check_or_show(data) {
    ////分析 wininit 的参数 status': 'protect_starting', 'protect_mode': 'out', 'timer_remain': 59

    win_protect_starting_inittime = (new Date().getTime()) / 1000;
    win_protect_starting_init_time_remained = data.remain_second;

    win_protect_starting_protectmode = data.house_status_chs;
	if (data.house_status == "outgoing") 
		win_protect_starting_protectmode = "外出";
	else if (data.house_status == "indoors")
		win_protect_starting_protectmode = "居家";
	else
		win_protect_starting_protectmode = "未知";
	//console.error("data.house_status_chs() data.house_status() win_protect_starting_protectmode() ")

	win_protect_starting_init("");
	if (ui_state_current_shown == 'protect_starting') return 0;

    $('#protect_starting').on('shown.bs.modal', function() {
        win_protect_starting_init("all");
		system_close_last_window('protect_starting');
    });
    return 1;

}

function win_protect_starting_init(ispart) {
    $('#protect_starting_status').html("即将进入" + win_protect_starting_protectmode + "保护模式");
	$('#protect_starting_btn-cancel').on('click', function() {
		audio_system_play_click();
        win_protect_starting_submit("cancel")
    });
	if (ispart=="all")
	{
		$('#protect_starting_timeremain').html("<font face='兰亭黑' >"+win_protect_starting_init_time_remained+"</font>" );
		audio_system_play_time_warning();
		win_protect_starting_inittime = (new Date().getTime()) / 1000;
		win_protect_starting_timer = window.setTimeout(function() {
			win_protect_starting_timer_event();
		}, 1000);
	}


}
function win_protect_starting_stop() {
    $('#protect_starting_status').html();
    $('#protect_starting_timeremain').html();
    $('#protect_starting_btn-cancel').off('click');
    audio_system_stop_all();
	window.clearTimeout(win_protect_starting_timer);


}





///////////////      case "protected":
var win_protected_protectmode;


function win_protected_check_or_show(data) {
    ////分析 wininit 的参数'status': 'protected', 'protect_mode': 'out'
	win_protect_starting_protectmode = data.house_status_chs;
	if (data.house_status == "outgoing")
		win_protected_protectmode = "外出";
	else if (data.house_status == "indoors")
		win_protected_protectmode = "居家";
	else
		win_protected_protectmode = "未知";
    

	win_protected_init();

	if (ui_state_current_shown == 'protected') return 0;
    $('#' + data.status).on('shown.bs.modal', function() {
        system_close_last_window('protected');
    });

    $('#' + data.status).on('show.bs.modal', function() {
        
    });

    return 1;
}
function win_protected_init() {
    $('#protected_status').html("已设防，" + win_protected_protectmode + "模式 ");
    $('#protected_btn-cancel').on('click', function() {
		//console.error("one two three");
		audio_system_play_click();
        win_unlock_protect_submit("start", "");
    });
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

function win_unlock_protect_submit(okorcancel, passwd) {
    //time_stamp = Math.floor((new Date().getTime()) / 60000);
	
    $.ajax({
        url: "http://"+g_vars_domain_prefix+"/set_cancel_protected",
        data: {
            mode: win_protected_protectmode,
            action: okorcancel,
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
    now_time = (new Date().getTime()) / 1000
    total_remain = Math.floor(win_unlock_protect_remain_seconds - (now_time - win_unlock_protect_inittime))
    console.error("in win_unlock_protect ", total_remain);
    $('#unlock_protect_remain_seconds').html(total_remain);
    if (total_remain > 0) {
        win_unlock_protect_timer = window.setTimeout(function() {
            win_unlock_protect_timer_event();
        }, 1000);
    } else{
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
	if (ui_state_current_shown == 'unlock_protect') return 0;


    $('#' + data.status).on('shown.bs.modal', function() {

		win_unlock_protect_inittime = (new Date().getTime()) / 1000;
        win_unlock_protect_timer = window.setTimeout(function() {
            win_unlock_protect_timer_event();
        }, 500);

        virual_password_keyboard_init("win_unlock_protect_input", function(pw) {
			win_unlock_protect_stop();
            win_unlock_protect_submit("ok", pw);
			
        });


		system_close_last_window('unlock_protect');

    });

    return 1;
}
function win_unlock_protect_stop() {
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

	$('#alert_message_explain').html(win_alert_message_explain);
    $('#alert_message_btn-stopalert').on('click', function() {
			audio_system_play_click();
            win_alert_message_submit(win_alert_message_alertid);
        });

	if (ui_state_current_shown == 'alert_message') return 0;

    $('#' + data.status).on('shown.bs.modal', function() {

		audio_system_play_alerm();
        system_close_last_window('alert_message');
    });
    $('#' + data.status).on('show.bs.modal', function() {
    });

    return 1;
}
function win_alert_message_stop() {
	$('#alert_message_explain').html();
    $('#alert_message_btn-stopalert').off('click');
}

///////////////      case "bell_ring":
var win_bell_ring_bellid;
var win_bell_ring_description;

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
			try { throw new Error("dummy"); } catch (e) { console.log(e.stack); }
            alert("网络连接异常！");
        }
    });
}




function win_bell_ring_check_or_show(data) {
    //分析 wininit  
    win_bell_ring_bellid = "453453452"
    win_bell_ring_description = "门铃"
	
   
	$('#bell_ring_description').html(win_bell_ring_description + "呼叫……");

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

    
	if (ui_state_current_shown == 'bell_ring') return 0;
    $('#' + data.status).on('shown.bs.modal', function() {
		audio_system_play_bell_ring();
        system_close_last_window('bell_ring');
    });
	$('#' + data.status).on('show.bs.modal', function() {
	});
    return 1;
}
function win_bell_ring_stop() {
	$('#bell_ring_description').html();

	$('#bell_ring_startstream').off('click');
	$('#bell_ring_opendoor').off('click');
	$('#bell_ring_reject').off('click');

}


///////////////      case "bell_view":
var win_bell_view_bellid;
var win_bell_view_video_url;

function win_bell_view_check_or_show(data) {
    //分析 wininit  
    win_bell_view_bellid = "453453452"
    win_bell_view_video_url = "1488879903612.mp4"
    

	//使用和相同的url submit
	$('#bell_view_opendoor').on('click', function() {
		audio_system_play_click();
		win_bell_ring_submit(win_bell_view_bellid, "opendoor");
	});
	$('#bell_view_reject').on('click', function() {
		audio_system_play_click();
		win_bell_ring_submit(win_bell_view_bellid, "reject");
	});

 	if (win_bell_view_video_url != "") {
		document.getElementById("bell_view_video").src = win_bell_view_video_url;
		document.getElementById("bell_view_video").play();
	}
    
	if (ui_state_current_shown == 'bell_view') return 0;
    $('#' + data.status).on('shown.bs.modal', function() {
        system_close_last_window('bell_view');
    });
	$('#' + data.status).on('show.bs.modal', function() {
	});
    return 1;
}
function win_bell_view_stop() {
	$('#bell_view_opendoor').off('click');
	$('#bell_view_reject').off('click');

	document.getElementById("bell_view_video").pause();
	document.getElementById("bell_view_video").src ="";


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