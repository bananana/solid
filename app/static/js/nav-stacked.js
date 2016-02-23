/******************************************************************************
 * Handle stacked navigation                                                  *
 ******************************************************************************/
$(document).ready(function() {
    // Listen for button clicks
    $('.nav-stacked a').on('click', function(e) {
        var currentSection = $(this).attr('href');
        $('.sections ' + currentSection).show().siblings().hide();
        $(this).parent('li').addClass('active').siblings().removeClass('active');
        e.preventDefault();
    });

    // If there's a hash passed in the URL, display that section
    var hash = window.location.hash;
    if(hash) {
        // Make user that button id's are of format: <name>-btn
        $(hash + '-btn').trigger('click');
    }
});
