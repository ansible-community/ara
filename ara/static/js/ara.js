$(document).ready(function(){
    $('.detail-link').click(function(e) {
        e.stopPropagation();
    });
    $(".task").click(function(){
        ele = $(this).closest('tr').next('tr');
        if (ele.css('display') == 'none')
            ele.css('display', 'table-row');
        else
            ele.css('display', 'none');
    });
    $(".results").click(function(){
        $(this).css('display', 'none');
    });
});
