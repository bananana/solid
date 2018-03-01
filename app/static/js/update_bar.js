/******************************************************************************
 * AJAX update bar
 ******************************************************************************/
$(document).ready(function () {
		$('form#post').ajaxForm(function() {
			window.location.hash = 'log';
			window.location.reload(true);
		});
});
