/******************************************************************************
 * Handle modals                                                              *
 ******************************************************************************/
$(document).ready(function () {
    // Event listener
    $('.button-modal, .button-modal-close').on('click', function() {
        var target = $('.button-modal').data('target');
        var visibility = $('#' + target).css('visibility') == 'hidden' ? 'visible' : 'hidden';
        $('#' + target).css('visibility', visibility); 
    });
});
