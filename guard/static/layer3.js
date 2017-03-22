//layer 3 control part--------------


/////////////  devices_view
var win_devices_view_item_per_page = 4;
var win_devices_view_curpageNo = 1;
var win_devices_view_devices_cache;
var win_devices_view_device_count=0;

function win_devices_view_updateui()
{
	    var strHTML = ""
        var ipagenum = 0;
        var item_num = 0;
		//
			win_devices_view_device_count=0;
			$.each(win_devices_view_devices_cache, function(index, val) {
				win_devices_view_device_count += 1;
			});
		//check curpageno is valid
		var maxpage= Math.floor(win_devices_view_device_count/win_devices_view_item_per_page);
		maxpage += win_devices_view_device_count%win_devices_view_item_per_page?1:0;
		if (win_devices_view_curpageNo > maxpage) win_devices_view_curpageNo = maxpage;

		console.log("device_count("+win_devices_view_device_count+") maxpage("+maxpage+")" ,win_devices_view_curpageNo);
		var pageno_base0 = win_devices_view_curpageNo -1;
		$.each(win_devices_view_devices_cache, function(index, val) {
            item_num += 1;
            if ((item_num > win_devices_view_item_per_page * pageno_base0) && 
				(item_num <= (win_devices_view_item_per_page * pageno_base0 + win_devices_view_item_per_page)))
			{
				console.log("draw item:",item_num, val.uuid, val.position, val.status, val.type)

                strHTML += "<tr><td>" + val.uuid.slice(-12,-1) + "</td>";
				strHTML += "<td>" + val.type + "</td>";
                strHTML += "<td> <button type='button' class='btn btn-info' onclick='win_modify_position_name_init(\"" + val.uuid + "\",\" " + val.position + "\")'>" + val.position + "</button></td></tr>";
                
            }

        });
        $('#devices_view_device_tr').html(strHTML);

		strHTML=""
		for (var i=1; i<=maxpage ; i++ )
		{
			if (i== win_devices_view_curpageNo)
			{
				strHTML+="<li><a style='color:#333333;' onclick='win_devices_view_gotopage("+i+");'>"+i+"</a></li>"
			}else
				strHTML+="<li><a onclick='win_devices_view_gotopage("+i+");'>"+i+"</a></li>"
		}
		$('#win_devices_view_pager').html(strHTML);
}
function win_devices_view_gotopage(ipage)
{
	
	win_devices_view_curpageNo = ipage;
	console.log("to draw page:" ,win_devices_view_curpageNo);
	win_devices_view_updateui();
}

$('#devices_view').on('show.bs.modal', function() {

	//$.ajax({
		$.getJSON("http://"+g_vars_domain_prefix+ "/get_status", //get_devices_list
			function(data)	
			{
				win_devices_view_devices_cache = JSON.parse(JSON.stringify(data["devices_status"]));
				win_devices_view_updateui();
			   
				
			});
});

/////////////  

/*win ui
win_modify_position_name_form
win-modify_position_name-uuid
win-modify_position_name-oldname
win_modify_position_name_Newname
win_modify_position_name_submit
*/
function win_modify_position_name_func_submit() {

	var newname=document.getElementById("win_modify_position_name_Newname").value;
	var oldname=document.getElementById("win-modify_position_name-oldname").value;
	var uuid=$('#win-modify_position_name-uuid').html();
	
	console.info("in win_modify_position_name_func_submit ", uuid,oldname,newname );
	if (newname=="")
		document.getElementById("win_modify_position_name_Newname").focus();
	else
	{
		  $.ajax({    
    							url: "http://"+g_vars_domain_prefix+"/set_device_alias",   
    							data:{    
    									 uuid:uuid,
    									 oldname:oldname,
    									 newname:newname
    							},    
    							type:'get',    
    							cache:false,    
    							dataType:'json',    
    							success:function(data) {    
										if (data["result"]=="ok")
										{
												win_devices_view_devices_cache = JSON.parse(JSON.stringify(data["devices_status"]));
												win_devices_view_updateui();
												win_modify_position_name_stop();
										}
										else{
											Popup_info_pop("提交数据失败", "show", 1200);
											win_modify_position_name_stop();
										}
    									  
    							 },    
    							 error : function() {    
    								  alert("网络连接异常！");    
    							 }    
    		});
    	
		
	}
}
function win_modify_position_name_stop() {
	$('#win_modify_position_name_submit').off("click");
	$('#modify_position_name').modal("hide");
}
function win_modify_position_name_init(uuid, positionname) {
    $('#win-modify_position_name-uuid').html(uuid);
    document.getElementById("win-modify_position_name-oldname").value = positionname;
	document.getElementById("win_modify_position_name_Newname").value ="";
    
	$('#win_modify_position_name_submit').on("click",function(){
		console.info("#win_modify_position_name_submit");
		win_modify_position_name_func_submit();
	});
	$('#modify_position_name').modal("show");


}








////////////////////////
var win_change_password_step=1;
var win_change_password_oldpw="";
var win_change_password_newpw="";
function win_change_password_submit(){
	//$.ajax({ ch_passwd
	Popup_info_pop("撤防密码已成功修改", "show", 800);
	$('#change_password').modal("hide");
}

function win_change_password_updateui(istep){
	if (istep  == 1)
	{
		virual_password_keyboard_close();
		$('#win_change_password_stepprompt').html("请输入当前撤防密码");
		virual_password_keyboard_init("win_change_password_input", function(pw) {
			if (pw == win_change_password_oldpw)
			{
				win_change_password_step=2;
				
			}else
				 Popup_info_pop("当前撤防密码输入错误", "show", 800);
			win_change_password_updateui(win_change_password_step);

		});
	}else if (istep  == 2){
		virual_password_keyboard_close();
		$('#win_change_password_stepprompt').html("请输入新的撤防密码");
		virual_password_keyboard_init("win_change_password_input", function(pw) {
			win_change_password_newpw = pw;
			win_change_password_step=3;
			win_change_password_updateui(win_change_password_step);

		});

	}else if (istep  == 3){
		virual_password_keyboard_close();
		$('#win_change_password_stepprompt').html("请再次输入新的撤防密码");
		virual_password_keyboard_init("win_change_password_input", function(pw) {
			if (pw == win_change_password_newpw)
			{
				 win_change_password_submit();
				
			}else{
				 Popup_info_pop("两次新的撤防密码输入不一致", "show", 800);
				 win_change_password_updateui(win_change_password_step);
			}

		});

	}

}
$('#change_password').on('show.bs.modal', function() {
	// $.ajax({
    $.getJSON("/get_protect_pw", function(data) {
		//hash = hex_md5("test");
        win_change_password_oldpw="123456";
    });
	win_change_password_oldpw="123456"; //for debug

	win_change_password_step=1;
	win_change_password_updateui(win_change_password_step);


});
$('#change_password').on('hidden.bs.modal', function() {
	  win_change_password_step=1;
	  win_change_password_oldpw="";
	  win_change_password_newpw="";
	  virual_password_keyboard_close();
});







/////////////////////
var win_popup_info_timer=0;
function Popup_info_pop(prompt, action, timeout) {
    console.log("run Popup_info_pop", prompt, action, timeout);

    //		document.getElementById("win-modify_position_name-oldname").value=positionname
    if (action == "show") {
        if (prompt == "loading") { //进行特别的专门项目进行转义
            $('#Popup_info_prompt').html("<i class='fa fa-circle-o-notch fa-spin fa-2x fa-fw'></i> <span >正在尝试与服务器连接......</span>");
        }
		else
			$('#Popup_info_prompt').html("<p style='color:#E0E020' class='fa fa-exclamation-triangle'></p><span>  "+ prompt+"</span>");

        $('#Popup_info').modal({
                backdrop: false
            })
            .modal("show");

		if (timeout > 0 )
		{
			win_popup_info_timer = window.setTimeout (function () {
							$('#Popup_info').modal("hide");
						},timeout);
		}


    } else if (action == "hide") {
        $('#Popup_info').modal(action);
    }


}
