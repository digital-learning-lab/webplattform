

$(".js-testimonialForm").on("submit", function(e) {
    e.preventDefault();
    var form = $(this);
    var actionUrl = form.attr('action');

    $.ajax({
        type: "POST",
        url: actionUrl,
        data: form.serialize(), // serializes the form's elements.
        success: function(data)
        {
            $(".js-testimonialSection .information-area__body").html("<p>Vielen Dank für Ihre Einreichung!</p>")
        },
        error: function(data) {
            $(".js-testimonialSection").replaceWith(data.responseText)
        }
    });

})
