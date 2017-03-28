


var keyboard_targetinput_id;
var keyboard_targetinput_callback;
function doInput()
{
	var output  = document.getElementById(keyboard_targetinput_id);
	var sHtml=this.innerHTML.replace(' ','');
	sHtml=sHtml.replace(/\<.*?\>/g,'');
	
	switch(sHtml)
	{
		case '=':
		case '+':
		case '-':
		case '×':
			break;
		case '删除':
			output.val = output.val.slice(0,-1);
			break;
		case '清空':
			output.val="";
			break;
		default:	//数字0-9
			value=parseInt(sHtml, 10);
			if (value>=0 && value<=9)
			{
				output.val += sHtml;
			}
			
			break;
	}
	console.log ("virual_password_keyboard Input: " + sHtml +" all is " +output.val )

	var $input = $("#"+keyboard_targetinput_id+" + div input"); 
	//console.log ("canprotect: "  + JSON.stringify($input) );
                
	var pwd = output.val.trim();  
	for (var i = 0, len = pwd.length; i < len; i++) {  
		$input.eq("" + i + "").val(pwd[i]);  
	}  
	$input.each(function() {  
		var index = $(this).index();  
		if (index >= len) {  
			$(this).val("");  
		}  
	});  
	if (len >= 6) {  
		keyboard_targetinput_callback(pwd.slice(0,6));
		//执行其他操作  
	}  
           	 
}


function virual_password_keyboard_init( target_id ,fun_callback ){
	var aLi=document.getElementsByTagName('li');
	var i=0;
	console.log ("virual_password_keyboard_init: " + aLi.length )
	for(i=0;i<aLi.length;i++)
	{
		if (aLi[i].id.substr(0,8) == "keyboard" ) 
		{
		
			aLi[i].onmousedown=doInput;
/*
			aLi[i].onmouseover=function ()
			{
				this.className='active';
			};
			
			aLi[i].onmouseout=function ()
			{
				this.className='';
			};
*/
		}
	}
	
	keyboard_targetinput_id		  = target_id;
	keyboard_targetinput_callback = fun_callback;
	document.getElementById(keyboard_targetinput_id).val="";

	var $input = $("#"+keyboard_targetinput_id+" + div input"); 
	for (var i = 0;  i < 6; i++) {  
		$input.eq("" + i + "").val("");  
	}  
}

function virual_password_keyboard_close(){

	var aLi=document.getElementsByTagName('li');
	//console.log ("virual_password_keyboard_close: " + aLi.length );
	var i=0;
	for(i=0;i<aLi.length;i++)
	{
		if (aLi[i].id.substr(0,8) == "keyboard" ) 
		{
		
			aLi[i].onmousedown="";
		}
	}
}