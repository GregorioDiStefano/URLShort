$(window).load(function(){
$("#enter_url").keyup(function (e) {
    if ($(this).val() == "") {
        $(".arrow_box").hide()
    }

    if (e.keyCode == 13) {
        var jqxhr = $.get( "/api?url=" + $("#enter_url").val(), function() {
        })
        .done(function(data) {
            $(".arrow_box").show()
            $("#url").text(data["url"]);
        })
        .fail(function() {
            alert( "error" );
        })
       .always(function() {
            //alert( "finished" );
       });
    }
})
})
