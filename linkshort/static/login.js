$(document).ready(function() {
	$("#loginButton").click( function () {
		login();
	});
	
	$("#signupButton").click( function () {
		signup();
	});
	
	hideDefaultText($("#usernameInput"));
	hideDefaultText($("#passwordInput"));
	hideDefaultText($("#newUsernameInput"));
	hideDefaultText($("#newPasswordInput"));
});

var login = function () {
	$.post("login", { username: $("#usernameInput").val(), password: $("#passwordInput").val() }, function (data) {
		console.log("data from ajax: " + data);
		$("body").html(data);
	})
}

var signup = function () {
	$.post("signup", { username: $("#newUsernameInput").val(), password: $("#newPasswordInput").val() }, function (data) {
		console.log("data from ajax: " + data);
		$("body").html(data);
	})
}

/**
 * Default text will disappear 
 **/
var hideDefaultText = function (textBox) {
	var defaultValue = textBox.val();
 	textBox.focus( function() {
		textBox.val( textBox.val() == defaultValue ? '' : textBox.val() );
		this.style.color="#000";
	});
  	textBox.blur( function() {
   		var value = textBox.val().trim();
		if(!value){
			textBox.val(defaultValue);
			this.style.color="#CCC";
		} else {
			textBox.val(value.replace("/^\s+|\s+$/g"));
		}
  	});
};