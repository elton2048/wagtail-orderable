$(function() {
    var order_header = $('th.column-index_order');
    var listing_tbody = $('.listing tbody');
    var listing_thead = $('.listing thead');
    var sorted_cols = listing_thead.find('th.sorted');
    order_header.find('a').addClass('text-replace').removeClass('icon icon-arrow-down-after icon-arrow-up-after');
    order_header.find('a').html('<span class="icon icon-order" aria-hidden="true"></span> Sort');
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

                // Build params keeping current filters if this view is a child modeladmin
                // eg: Books -> Chapters: we need to keep the current selected book
                var params = new URL(window.location.href).searchParams;
                var idx;
                if ($(this).data('idx') < ui.item.index()) {
                    idx = $(movedElement).prev().data('object-pk');
                    if (idx) {
                        params.set('after', idx);
                    }
                } else if ($(this).data('idx') > ui.item.index()) {
                    idx = $(movedElement).next().data('object-pk');
                    if (idx) {
                        params.set('before', idx);
                    }
                }

                // Post
                if (idx) {
                    $.ajax({
                        url: 'reorder/' + movedObjectId + '/?' + params.toString(),
                        success: function(data, textStatus, xhr) {
                            addMessage('success', '"' + movedObjectTitle + '" has been moved successfully.');
                        },
                        error: function(data, textStatus, xhr) {
                            addMessage('error', '"' + movedObjectTitle + '" could not be moved.');
                            listing_tbody.sortable("cancel");
                        }
                    });
                }
            }
        });
        listing_tbody.disableSelection();
    } else {
        $('.field-index_order .handle').remove();
        var a = order_header.find('a');
        a.attr('title', 'Enable ordering of objects');
        var href = new URL(window.location.href);  // we need to keep current filters
        href.searchParams.set('o', '0');
        a.attr('href', href.toString());
        order_header.removeClass('sorted ascending');
    }
});
