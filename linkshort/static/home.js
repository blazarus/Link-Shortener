$(document).ready(function() {
	$("#shortenButton").click( function () {
		if ($("#originalUrlText").val()) {
			$.getJSON("shorten", 
						{ 
							original_url: $("#originalUrlText").val() 
						}, 
						function (data) {
				jsonCallback(makeLinkDiv, data);
			});
		} else {
			var message = "The URL cannot be blank!"
			console.log(message);
			$("#messagesContainer").text(message);
		}
	});
	$("#customizeButton").click( function () {
		$("#customizeButton").css({
			display:"none"
		});
		$("#customizeForm").css({
			display:"block"
		});
	});
	$("#submitCustomButton").click( function () {
		var invalidCustom = /([^A-Za-z0-9-])/.test($("#customUrlText").val());
		console.log ("is the custom url invalid? " + invalidCustom );
		
		if ($("#customUrlText").val() && $("#originalUrlText").val() && !invalidCustom) {
			$.getJSON("shorten/custom", 
						{ 
							original_url: $("#originalUrlText").val(),
							custom_shortened_url: $("#customUrlText").val()
						}, 
						function (data) {
				jsonCallback(makeLinkDiv, data);
			});
		} else {
			var message = "Enter a URL and your shortened URL link. The custom URL can consist of letters, numbers, and hyphens."
			console.log(message);
			$("#messagesContainer").text(message);
		}
	});

	$.getJSON("getLinks", function (data) {
		jsonCallback(buildLinkList, data);
	});
	
	/**
	* Takes the function to be called on success as a param
	* Standardizes the displaying of error messages
	*/
	var jsonCallback = function (func, data) {
		console.log("Data received from ajax: " + data);
		if (data.success) {
			func(data);
		} else {
			var message = "";
			if (data.error) {
				message = data.error;
			} else {
				message = "There was an error processing your request";
			}
			console.log(message);
			$("#messagesContainer").text(message);
		}
	}
	
	
	var buildLinkList = function (data) {
		var data = data.content;
		for (var x in data) {
			makeLinkDiv(data[x]);
		}
	}
	
	var makeLinkDiv = function (item) {
		var createdLinkDiv = $("<div>")
			.attr("class","createdLinkContainer");
		var shortenedLink = $("<a>")
				.attr("href",window.location.href+item.shortened_url)
				.attr("class","shortLinkDisplay")
				.text(window.location.href+item.shortened_url);
		var originalLink = $("<span>").attr("class","originalLink")
				.text(item.original_url);
		var analytics = $("<span>").attr("class","linkAnalytics")
				.text(item.num_redirects_last_day);
				
		$("#userUrlList").prepend(createdLinkDiv.append(shortenedLink).append(originalLink).append(analytics));
	}
});
