function makeScannedMailDestination() {
	$.ajax({
		url: "/get-scanned-mail-folder",
		type: "GET",
		data: {"author": {{ author }} },
		success: function(response) {
			parent.postMessage('close', '*');
		}
	});
}

$(document).ready(function () {
	$("#btnScannedMail").on("click", makeScannedMailDestination);
});