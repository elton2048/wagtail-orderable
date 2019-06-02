$(function() {
    var order_header = $('th.column-index_order');
    var listing_tbody = $('.listing tbody');
    var listing_thead = $('.listing thead');
    var sorted_cols = listing_thead.find('th.sorted');
    order_header.find('a').addClass('text-replace icon-order').removeClass('icon-arrow-down-after icon-arrow-up-after');

    if(sorted_cols.length == 1 && order_header.hasClass('sorted') && order_header.hasClass('ascending')){
        order_header.find('a').attr('title', 'Restore default list ordering').attr('href', '?');
        listing_tbody.sortable({
            cursor: "move",
            tolerance: "pointer",
            containment: "parent",
            handle: ".handle",
            items: "> tr",
            axis: "y",
            placeholder: "dropzone",
            start: function(event, ui){
                $(this).parent().addClass('sorting');
                $(this).data('idx', ui.item.index());
            },
            stop: function(event, ui){
                $(this).parent().removeClass('sorting');

                // Work out what page moved and where it moved to
                var movedElement = $(ui.item[0]);
                var movedObjectId = movedElement.data('object-pk');
                var movedObjectTitle = movedElement.find('td.field-index_order').data('title');

                // Build params
                var params;
                if ($(this).data('idx') < ui.item.index()) {
                    var after = $(movedElement).prev().data('object-pk');
                    if (after) {
                        params= "?after=" + after;
                    }
                } else if ($(this).data('idx') > ui.item.index()){
                    var before = $(movedElement).next().data('object-pk');
                    if (before) {
                        params = "?before=" + before;
                    }
                }

                // Post
                if (params) {
                    var url = "reorder/" + movedObjectId + '/' + params;
                    $.get(url, function(){
                        addMessage('success', '"' + movedObjectTitle + '" has been moved successfully.');
                    });
                }
            }
        });
        listing_tbody.disableSelection();
    } else {
        $('.field-index_order .handle').remove();
        order_header.find('a').attr('title', 'Enable ordering of objects').attr('href', '?o=0');
    }
});
