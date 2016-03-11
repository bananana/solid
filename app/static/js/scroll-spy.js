/******************************************************************************
 * Minimalistic scroll spy implementation based on JSFiddle by Marcus Ekwall  *
 * https://jsfiddle.net/mekwall/up4nu/                                        *
 ******************************************************************************/
$(document).ready(function() {
    // Target menu
    var menu = $('#nav-submenu');
    var menuContainer = $('#scrollspy');

    // Find all sections to be used in scroll spy
    var sections = $('.scrollspy-section');
    var sectionNames = sections.map(function() {
            return $(this).text();
        });
    var sectionIds = sections.map(function() {
            return $(this).find('a').attr('id');
        });

    // How much the scrollspy will be offset from the top
    var topOffset = 190;
    
    // Selectors
    var lastId,
        menuHeight = menu.outerHeight() + 20,
        menuItems = menu.find('a'),
        scrollItems = menuItems.map(function() {
            var item = $($(this).attr('href'));
            if (item.length) { return item; }
        });

    // Automatically generate the sidemenu
    for (i = 0; i < sections.length; i++) {
        menu.append('<li><a href="#' + sectionIds[i] + '">' + sectionNames[i] + '</a></li>');
    }
 
    // Event handler
    menuItems.click(function(e) {
        var href = $(this).attr('href'),
            offsetTop = href === '#' ? 0 : $(href).offset().top - menuHeight + 1;
        $('html, body').stop().animate({
            scrollTop: offsetTop
        }, 300);
        e.preventDefault();
    });

    // Bind to scroll
    $(window).scroll(function() {
        // Get container scroll position
        var position = $(this).scrollTop();
        var fromTop = position + menuHeight;
        
        // Get id of current scroll item
        var cur = scrollItems.map(function() {
            if ($(this).offset().top < fromTop) {
                return this;
            }
        });

        // Get the id of the current element
        cur = cur[cur.length - 1];
        var id = cur && cur.length ? cur[0].id : "";

        if (lastId !== id) {
            lastId = id;

            // Set or remove active class
            menuItems
                .parent().removeClass('active')
                .end().filter('[href="#' + id + '"]').parent().addClass('active');
        }

        // Make the scrollspy sticky when user scrolls beyond a certain point
        if (position > topOffset) {
            menuContainer.addClass('nav-stacked-fixed');
        }
        if (position < topOffset) {
            menuContainer.removeClass('nav-stacked-fixed');
        }
    });
});
