/******************************************************************************
 * Handle modals                                                              *
 ******************************************************************************/
$(document).ready(function () {
    // Event listener
    $('.button-modal').on('click', function(e) {
        var target = $(this).data('target');
        $('#' + target).toggle();
    });

