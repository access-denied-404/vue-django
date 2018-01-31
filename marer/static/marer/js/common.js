$(function () {
    $('body').on('click', '.spinjs', function (e) {
        var check = $('.check');
        if (check.length > 0) {
            if (check.val() !== 'blank') {
                setTimeout(function () {
                    $('body').append($('<img>', {
                        src: '/static/marer/img/rolling.gif',
                        style: 'position: fixed; border: 1px solid #ccc;width: 80px; z-index: 999; top: 45%; left: 50%;background: rgba(255, 255, 255, 0.75); padding: 5px;'
                    }));
                }, 1);
            } else {
                event.preventDefault();
            }
        } else {
            setTimeout(function () {
                    $('body').append($('<img>', {
                        src: '/static/marer/img/rolling.gif',
                        style: 'position: fixed; border: 1px solid #ccc;width: 80px; z-index: 999; top: 45%; left: 50%;background: rgba(255, 255, 255, 0.75); padding: 5px;'
                    }));
                }, 1);
        }
    })
});