/******************************************************************************
 * Handle modals                                                              *
 ******************************************************************************/
$(document).ready(function () {
    // Event listener
    $('[data-target^="modal"]').on('click', function(e) {
        var $a = $(e.target),
            $target = $('#' + $a.data('target'));

        $target.css('visibility', 'visible'); 

        if($a.attr('href')) {
            var $_a = $('<a>');
            $_a.attr('href', $a.attr('href'));
            $_a.text($a.text());
            $target.find('div').append($_a);
        }

        return false;
    });
    $('.button-modal-close').on('click', function(e) {
        $($(e.target).parents('.modal')[0]).css('visibility', 'hidden');
    });
});
