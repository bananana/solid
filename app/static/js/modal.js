/******************************************************************************
 * Handle modals                                                              *
 ******************************************************************************/
$(document).ready(function () {
    // Open
    function open(e) {
        var $a = $(e.currentTarget),
            $target = $('#' + $a.data('target'));

        $target.css('visibility', 'visible'); 

        if($a.attr('href')) {
            var $_a = $('<a>');
            $_a.attr('href', $a.attr('href'));
            $_a.text($a.text());
            $target.find('div').append($_a);
        }

        window.location.hash = '' + $a.data('target');
    }

    // Close 
    function close(e) {
        $($(e.target).parents('.modal')[0]).css('visibility', 'hidden');
    }

    // Event listeners 
    $('[data-target^="modal"]').on('click', open);
    $('.button-modal-close').on('click', close);

    // Open modals with URL hash
    var hash = window.location.hash.substring(1);
    if(hash) {
        $('[data-target="' + hash + '"]').click();
    }
});
