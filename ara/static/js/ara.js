$(document).ready(function () {
    // Toggle dropdown menu
    $(".list-view-pf-actions").on("show.bs.dropdown", function () {
        var $this = $(this);
        var $dropdown = $this.find(".dropdown");
        var space = $(window).height() - $dropdown[0].getBoundingClientRect().top - $this.find(".dropdown-menu").outerHeight(true);
        $dropdown.toggleClass("dropup", space < 10);
    });

    // Compound expansion
    $(".list-view-pf-expand").on("click", function () {
        var $this = $(this);
        var $heading = $(this).parents(".list-group-item");
        //var $row = $heading.parent();
        var $subPanels = $heading.find(".list-group-item-container");
        var index = $heading.find(".list-view-pf-expand").index(this);

        // Remove all active status
        $heading.find(".list-view-pf-expand.active").find(".fa-angle-right").removeClass("fa-angle-down")
          .end().removeClass("active")
            .end().removeClass("list-view-pf-expand-active");

        // Add active to the clicked item
        $(this).addClass("active")
          .parents(".list-group-item").addClass("list-view-pf-expand-active")
            .end().find(".fa-angle-right").addClass("fa-angle-down");

        // Check if it needs to hide
        if($subPanels.eq(index).hasClass("hidden")) {
            $heading.find(".list-group-item-container:visible").addClass("hidden");
            $subPanels.eq(index).removeClass("hidden");
        } else {
            $subPanels.eq(index).addClass("hidden");
            $heading.find(".list-view-pf-expand.active").find(".fa-angle-right").removeClass("fa-angle-down")
              .end().removeClass("active")
                .end().removeClass("list-view-pf-expand-active");
        }
    });

    // Click close button to close the panel
    $(".list-group-item-container .close").on("click", function () {
        var $this = $(this);
        var $panel = $this.parent();

        // Close the container and remove the active status
        $panel.addClass("hidden")
          .parent().removeClass("list-view-pf-expand-active")
            .find(".list-view-pf-expand.active").removeClass("active")
              .find(".fa-angle-right").removeClass("fa-angle-down")
    });

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Highlight the anchor line in file views
    var hash = $(location).attr('hash');
    $(hash).closest('span').addClass('hll');

    // Refresh the highlighted line when clicking on a new line in file views
    $('a').click(function(){
        $("span.hll").removeClass('hll');
        var hash = $(this).attr('href');
        $(hash).closest('span').addClass('hll');
    });
});
