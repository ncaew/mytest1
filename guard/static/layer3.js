//layer 3 control part--------------

  var GetLength = function (str) {
    ///<summary>获得字符串实际长度，中文2，英文1</summary>
    ///<param name="str">要获得长度的字符串</param>
    var realLength = 0, len = str.length, charCode = -1;
    for (var i = 0; i < len; i++) {
      charCode = str.charCodeAt(i);
      if (charCode >= 0 && charCode <= 128) realLength += 1;
      else realLength += 2;
    }
    return realLength;
  };
 
  //js截取字符串，中英文都能用 
  //如果给定的字符串大于指定长度，截取指定长度返回，否者返回源字符串。 
  //字符串，长度 
 
  /** 
   * js截取字符串，中英文都能用 
   * @param str：需要截取的字符串 
   * @param len: 需要截取的长度 
   */
  function cutstr(str, len) {

	if (GetLength(str) <= len)  
	{
		return str;
	}
    var str_length = 0;
    var str_len = 0;
    str_cut = new String();
    str_len = str.length;
    for (var i = 0; i < str_len; i++) {
      a = str.charAt(i);
      str_length++;
      if (escape(a).length > 4) {
        //中文字符的长度经编码之后大于4 
        str_length++;
      }
      str_cut = str_cut.concat(a);
      if (str_length >= len) {
        str_cut = str_cut.concat("...");
        return str_cut;
      }
    }
    //如果给定字符串小于指定长度，则返回源字符串； 
    if (str_length < len) {
      return str;
    }
  }
  
 

/////////////  devices_view
var win_devices_view_item_per_page = 5;
var win_devices_view_curpageNo = 1;
var win_devices_view_devices_cache;
var win_devices_view_device_count=0;
var win_devices_view_isopen=0;


function win_modify_position_name_func_submit(uuid,attr, value) {
 
	var post_date = JSON.parse('{"uuid":"","posname":"","aliasname":"","outdoor":"","inhome":""}');

	console.log(uuid,attr, value);
	post_date["uuid"]=uuid;
	post_date[attr]=value;
	/*switch (attr)
	{
		case "posname":
			post_date["posname"]=value;
		case "aliasname":
			post_date["aliasname"]=value;
		case "outdoor":
			post_date["outdoor"]=value;
		case "inhome":
			post_date["inhome"]=value;
	}
	*/
	console.log (post_date);

	 
	//Popup_info_pop("上传数据修改", "show", 0);
	$.ajax({ url: "http://"+g_vars_domain_prefix+"/set_device_attr",   
		type:'get',    
		cache:false,
		data: post_date,
		async: true,
		dataType:'json',    
		success:function(data) {    
				if (data["result"].toLowerCase()=="ok")
				{
					/*
					 setTimeout(function() {
							Popup_info_pop("修改别名成功", "show", 1200);
					}, 500);
						*/
						win_devices_view_devices_cache = JSON.parse(JSON.stringify(data["devices_status"]));
						win_devices_view_updateui();
 
				}
				else{
					 setTimeout(function() {
							Popup_info_pop("修改设备属性失败", "show", 1200);
					}, 500);
					

				}
				  
		 },    
		 error : function() {    
			  alert("网络连接异常！");    
		 }  ,
		 complete: function(data) {
			 //Popup_info_pop("", "hide", 0);
		 }
	});


	 
} 
function dv_check(uuid , attr, value)
{
	if (value == "mycheck-switch-off") 
	{
		value="false";
	}
	else if(value == "mycheck-switch-on")
	{
		value="true";
	}
	win_modify_position_name_func_submit(uuid , attr, value );
}
function win_devices_view_update_status(json_data)
{
	//console.error("in win_devices_view_update_status" , win_devices_view_isopen);
	if (win_devices_view_isopen != 1)
		return ;
	var devices_cache = JSON.parse(JSON.stringify(json_data["devices_status"]));
	$.each(devices_cache, function(index, val) {
			element_id= "status-"+val.uuid;
			//console.error("in win_devices_view_update_status" ,element_id ,val.status, $('#'+element_id),$('#'+element_id).html());
			if ( $('#'+element_id).html()  !== undefined && $('#'+element_id).html() != val.status )
			{
				console.info("win_devices_view_update_status" ,val.uuid ,val.status, "oldv=" ,$('#'+element_id).html() );
				$('#'+element_id).html(val.status);
				
			}
	});
        
}
function mycheck_switch(ele)
{
   if (ele.value == 'mycheck-switch-on' ){
		ele.value='mycheck-switch-off';
   }else{
		ele.value='mycheck-switch-on';
   }
   console.log(ele, $(ele))
   $(ele).trigger('change');
}
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
				console.log("draw item:",item_num, val.uuid, val.type,  val.position, val.con_alert_outdoor ,val.con_alert_indoor, val.status );
				strTEMP =  " <tr > 	 <td><span style='color:#c1c1c1'>"+cutstr(val.type,12)+"</span></td> "+
							  "<td>  <input type='text'     onChange='dv_check(\""+val.uuid+"\",\"posname\", this.value  );' class='position-name-class' tabIndex=1  id='position_name' value='"+ val.position+ "'></td>"+
							  "<td>  <button type='button' onChange='dv_check(\""+val.uuid+"\",\"outdoor\",this.value);' onclick='mycheck_switch(this);'  value='mycheck-switch-" +( val.con_alert_outdoor == "true"?"on":"off")+ "' tabIndex=2 /></td>"+
							  "<td>  <button type='button' onChange='dv_check(\""+val.uuid+"\",\"inhome\",this.value);'  onclick='mycheck_switch(this);'  value='mycheck-switch-" +(  val.con_alert_indoor == "true"?"on":"off")+ "' tabIndex=3 /></td>"+
							  "<td><span id=status-"+val.uuid+">"+val.status+" </span></td>"+
							 "</tr> ";
				console.log("draw item:",strTEMP);
				strHTML += strTEMP;
                //strHTML += "<tr><td>" + val.uuid.slice(-12,-1) + "</td>";
				//strHTML += "<td>" + val.type + "</td>";
               // strHTML += "<td> <button type='button' class='btn btn-info' onclick='win_modify_position_name_init(\"" + val.uuid + "\",\" " + val.position + "\")'>" + val.position + "</button></td></tr>";
                
            }

        });
        $('#devices_view_device_tr').html(strHTML);
 
		strHTML=''
		//for (var i=1; i<=maxpage ; i++ )
		//{
		//	if (i== win_devices_view_curpageNo)
		//	{
		//		strHTML+="<li><a style='color:#333333;' onclick='win_devices_view_gotopage("+i+");'>"+i+"</a></li>"
		//	}else
		//		strHTML+="<li><a onclick='win_devices_view_gotopage("+i+");'>"+i+"</a></li>"
		//}
		if (win_devices_view_curpageNo <= 1){
			strHTML=	"<button class='pi-device-lastpage' disabled> </button> "
		}
		else{
			strHTML=	"<button class='pi-device-lastpage'  onclick='win_devices_view_gotopage("+ (win_devices_view_curpageNo-1) +");'> </button> "
		}
		strHTML += "<span class='pi-device-pagenum'>"+win_devices_view_curpageNo+" / "+maxpage+"</span>" 
		if (win_devices_view_curpageNo >= maxpage){
			strHTML +=	"<button class='pi-device-nextpage' disabled> </button> "
		}
		else{
			strHTML +=	"<button class='pi-device-nextpage'  onclick='win_devices_view_gotopage("+ (win_devices_view_curpageNo+1) +");'> </button> "
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
	win_devices_view_isopen =1;
	$.ajax({  url: "http://"+g_vars_domain_prefix+ "/get_devices_list",
        type: 'get',
        cache: false,
		//async: false,
        dataType: 'json',
        success: function(data) {
            	win_devices_view_devices_cache = JSON.parse(JSON.stringify(data["devices_status"]));
				win_devices_view_updateui();
        },
        error: function() {
			alert("网络连接异常！");
        }
    });

});
$('#devices_view').on('hide.bs.modal', function() {
 win_devices_view_isopen = 0;
});







////////////////////////
var win_change_password_step=1;
var win_change_password_oldpw="";
var win_change_password_newpw="";
function win_change_password_submit(oldpw,newpw){
	//$.ajax({ ch_passwd
	$.ajax({ url: "http://"+g_vars_domain_prefix+"/ch_passwd",   
			type:'get',    
			data: {
				oldpw: oldpw,
				newpw: newpw
			},
			cache:false,
			async: false,
			dataType:'json',    
			success:function(data) {    
					
					if (typeof data["result"] === "string" && data["result"].toLowerCase()=="ok")
					{
						Popup_info_pop("撤防密码已成功修改", "show", 2000);
					}else{
						Popup_info_pop("撤防密码修改失败", "show", 2000);
					}
 			 },    
			 error : function() {    
					Popup_info_pop("撤防密码修改失败", "show", 2000);  
			 }  ,
			 complete: function(data) {
					$('#change_password').modal("hide");
			 }
	});


	
}

function win_change_password_updateui(istep){
	if (istep  == 1)
	{
		virual_password_keyboard_close();
		$('#win_change_password_stepprompt').html("请输入当前撤防密码");
		virual_password_keyboard_init("win_change_password_input", function(pw) {
			console.log("passwd:old and input",win_change_password_oldpw,hex_md5(pw).toLowerCase());
			if (typeof(win_change_password_oldpw) == "undefined") //logic if no get oldpw , 
			{
				win_change_password_oldpw = hex_md5(pw).toLowerCase();
			}
			if (hex_md5(pw).toLowerCase() == win_change_password_oldpw)
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
				 win_change_password_submit(win_change_password_oldpw,win_change_password_newpw);
				
			}else{
				 Popup_info_pop("两次新的撤防密码输入不一致", "show", 800);
				 win_change_password_updateui(win_change_password_step);
			}

		});

	}

}
$('#change_password').on('show.bs.modal', function() {
	//acqure passwd 
	$.ajax({ url: "http://"+g_vars_domain_prefix+"/get_protect_pw",   
			type:'get',    
			cache:false,
			async: false,
			dataType:'json',    
			success:function(data) {    
					win_change_password_oldpw=data["password"];
 			 },    
			 error : function() {    
				  win_change_password_oldpw=undefined;
				  alert("网络连接异常！");    
			 }  ,
			 complete: function(data) {
				 //Popup_info_pop("", "hide", 0);
			 }
	});


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
