function printerAPI(id,action) {
	var params="";
	for( var i=0; i<document.getElementById("printerForm").elements.length; i++ )
	{
	   var fieldName = document.getElementById("printerForm").elements[i].name;
	   var fieldValue = document.getElementById("printerForm").elements[i].value;

	   params += fieldName + '=' + fieldValue + '&';
	}	
	if (action == "expire") {
		ed=document.getElementById("dateoutday").value();
		em=document.getElementById("dateoutmonth").value().split(" ")[0];
		ey=document.getElementById("dateoutyear").value();
		pd=document.getElementById("dateinday").value().split(" ")[0];
		pm=document.getElementById("dateinmonth").value();
		py=document.getElementById("dateinyear").value();
		params+="packed="+pd+"-"+pm+"-"+py;
		if (document.getElementById("expireVisible").checked()) {
			params+="&expired="+ed+"-"+em+"-"+ey;
		}
	}
	if (window.XMLHttpRequest) { printerAPICall=new XMLHttpRequest(); }
	else { printerAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	printerAPICall.onreadystatechange=function() {
		if (printerAPICall.readyState==4 && printerAPICall.status==200) {
			var result=printerAPICall.responseText;		
			var values=JSON.parse(result);	
			if(values.result=="success"){	
				document.getElementById("printerOutput").innerText=values.reason;
			}
			else{
				document.getElementById("printerOutput").innerText=values.reason;
			}
		}
	}
	printerAPICall.open("POST","/print/"+action+"?r="+Math.random(),true);
	printerAPICall.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	printerAPICall.send(params);	
	if (action=="archive") {
		var zero="0"
		if (document.getElementById("autoCode").checked == true) {
			let val=parseInt(document.getElementById("archiveCode").value, 10) + 1;
			document.getElementById("archiveCode").value=zero.repeat(5 - val.toString().length)+val.toString();
		}
	}
	return false;
}

function manageAPI(id,action) {
	var params="";
	if (action == "config/save") {
		for( var i=0; i<document.getElementById("configForm").elements.length; i++ )
		{
		   var fieldName = document.getElementById("configForm").elements[i].name;
		   var fieldValue = document.getElementById("configForm").elements[i].value;
		   params += fieldName + '=' + fieldValue + '&';
		}	
	}
	for( var i=0; i<document.getElementById("manageForm").elements.length; i++ )
	{
	   var fieldName = document.getElementById("manageForm").elements[i].name;
	   var fieldValue = document.getElementById("manageForm").elements[i].value;
	   params += fieldName + '=' + fieldValue + '&';
	}	
	if (window.XMLHttpRequest) { manageAPICall=new XMLHttpRequest(); }
	else { manageAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	manageAPICall.onreadystatechange=function() {
		if (manageAPICall.readyState==4 && manageAPICall.status==200) {
			var result=manageAPICall.responseText;		
			var values=JSON.parse(result);	
			if(values.result=="success"){	
				document.getElementById("manageOutput").innerText=values.reason;
				if(values.datas) {
					document.getElementById("configModel").value=values.datas['printer']['model'];
					document.getElementById("configUSB").value=values.datas['printer']['usb'];
					document.getElementById("configSerial").value=values.datas['printer']['serial'];
				}
			}
			else{
				document.getElementById("manageOutput").innerText=values.reason;
			}
		}
	}
	document.getElementById("manageOutput").innerText="Request the action to system..."
	manageAPICall.open("POST","/manage/"+action+"?r="+Math.random(),true);
	manageAPICall.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	manageAPICall.send(params);	
	if (action=="update") {
		setTimeout("updateAPI('updateOutput')",2000);
	}
	return false;
}

function updateAPI(id) {
	var params="";
	for( var i=0; i<document.getElementById("manageForm").elements.length; i++ )
	{
	   var fieldName = document.getElementById("manageForm").elements[i].name;
	   var fieldValue = document.getElementById("manageForm").elements[i].value;
	   params += fieldName + '=' + fieldValue + '&';
	}	
	if (window.XMLHttpRequest) { updateAPICall=new XMLHttpRequest(); }
	else { updateAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	updateAPICall.onreadystatechange=function() {
		if (updateAPICall.readyState==4 && updateAPICall.status==200) {
			var result=updateAPICall.responseText;
			document.getElementById("updateOutput").innerText=result;
			setTimeout("updateAPI('updateOutput')",2000);
			document.getElementById("updateOutput").scrollTop = document.getElementById("updateOutput").scrollHeight;
		}
	}
	updateAPICall.open("POST","/manage/update/log?r="+Math.random(),true);
	updateAPICall.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	updateAPICall.send(params);	
	return false;
}

function loadImages(id) {
	if (window.XMLHttpRequest) { loadImagesAPICall=new XMLHttpRequest(); }
	else { loadImagesAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	loadImagesAPICall.onreadystatechange=function() {
		if (loadImagesAPICall.readyState==4 && loadImagesAPICall.status==200) {
			var result=loadImagesAPICall.responseText;	
			var values=JSON.parse(result);	
			document.getElementById("imageList").innerHTML="";
			for (var i=0; i<values.images.length; i++){
				document.getElementById("imageList").innerHTML+='<option value="images/'+values.images[i]+'">'+values.images[i]+'</option>';
			}
		}
	}
	loadImagesAPICall.open("GET","/api/images?r="+Math.random(),true);
	loadImagesAPICall.send();	
	return false;
}
function changeImage() {
	document.getElementById("textimagePreview").src=document.getElementById("imageList").value.replace("images/","api/image/");
}