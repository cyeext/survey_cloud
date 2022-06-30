(function (jq) {
    jq('.dynamic-menu .title').click(function () {
        $(this).next().toggleClass('hide');
    });
})(jQuery);