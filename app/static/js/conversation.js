/******************************************************************************
 * Handle converstions                                                        *
 ******************************************************************************/
$(document).ready(function () {
    var heightConstraint = 85;

    $('.post article').each(function () {
        // Insert "more" button only for posts that exceed heightConstraint.
        if($(this).height() > heightConstraint) {
            $(this).css('height', heightConstraint);
            $(this).append('<div class="fade">' +
                           '    <small>' + 
                           '        <a data-target="' + $(this).attr('id') + '">' + 
                           '            More&nbsp;<img class="icon" src="/static/open-iconic/png/caret-bottom-2x.png">' + 
                           '        </a>' + 
                           '    </small>' + 
                           '</div>');
        }
        else {
            $(this).css('height', heightConstraint);
        }
    });

    $('.post article .fade small a').click(function () {
        articleBody = $('#' + $(this).attr('data-target'))

        if (articleBody.height() == heightConstraint) {
            var curHeight = articleBody.height(),
                autoHeight = articleBody.css('height', 'auto').height();

            articleBody.height(curHeight);

            // Actual easing and animation speed are controlled by [.post article] class in app/static/css/custom.css
            articleBody.animate({height: autoHeight}, 0, 'linear');
            $('#' + articleBody.attr('id') + ' .fade a').html('Less&nbsp;<img class="icon" src="/static/open-iconic/png/caret-top-2x.png">');
        }
        else {
            articleBody.animate({height: heightConstraint}, 0, 'linear');
            $('#' + articleBody.attr('id') + ' .fade a').html('More&nbsp;<img class="icon" src="/static/open-iconic/png/caret-bottom-2x.png">');
        }
    });
});
