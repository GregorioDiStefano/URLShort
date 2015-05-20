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
            if (jqxhr.status == 403)
                $("#url").text("limited exceeded, try again later")
            else
                $("#url").text("error -- try again")
        })
       .always(function() {
            //alert( "finished" );
       });
    }
})
})

$(document).ready(function() {
    $("#login").hide()
    $("#login_failed").hide()

    $("#login > span, #login_link").click(function() {
        $("#login").toggle()
    })

    $("#login_btn").click(function() {
        $.post( "/login", $( "#login_form" ).serialize() )
            .done(function(data) {
                if (data.pass) {
                    $("#login_failed").hide()
                    alert("pass")
                } else if (data.fail) {
                    $("#login_failed").show()
                }
            })
            .fail(function(data) {
                alert("Ouch! Looks like the site is having problems");
            })

    })
})
