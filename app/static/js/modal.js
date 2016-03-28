/******************************************************************************
 * Handle modals                                                              *
 ******************************************************************************/
$(document).ready(function () {
    // Event listener
    $('.button-modal').on('click', function() {
        var target = $(this).data('target');
        $('#' + target).css('visibility', $('#' + target).css('visibility') == 'hidden' ? 'visible' : 'hidden'); 
    });
});
