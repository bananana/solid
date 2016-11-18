/******************************************************************************
 * Send language code to Flask and Babel                                      *
 ******************************************************************************/
function translate(translateTo) {
    $.post('/translate', { 
            lang_code: translateTo
    }).done(function() {
        location.reload();
    });
}
