/******************************************************************************
 * Handle dropdowns, they must have on click events for mobile                *
 ******************************************************************************/

$(document).ready(function () {
    $('#lang-dropdown').click(function () {
        $('#lang-dropdown > .dropdown-button').toggleClass('dropdown-button-click');
        $('#lang-dropdown > .dropdown-content').toggleClass('dropdown-content-click');
    });
    $('#main-menu').click(function() {
        $('#main-menu > .dropdown-button').toggleClass('dropdown-button-click');
        $('#main-menu > .dropdown-content').toggleClass('dropdown-content-click');
    });
});
