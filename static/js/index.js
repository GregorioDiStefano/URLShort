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
    $("#signup_failed").hide()
    $("#signup").hide()

    if (user_logged_in)
        logged_in()

    $("#login > span, #login_link").click(function() {
        if ($("div#signup").is(':visible')) {
            $("div#signup").hide()
        }
        $("#login").toggle()
    })

    $("#logout_link").click(function() {
        $.get("/logout")
        logged_out()
    })

    $("#signup > span, #signup_link").click(function() {
        if ($("div#login").is(':visible')) {
            $("div#login").hide()
        }
        $("#signup").toggle()
    })

    $("#login_btn").click(function() {
        $.post( "/login", $( "#login_form" ).serialize() )
            .done(function(data) {
                if (data.pass) {
                    $("#login_failed").hide()
                    var email = $("#login_email").val()
                    logged_in(email)
                } else if (data.fail) {
                    $("#login_failed").show()
                }
            })
            .fail(function(data) {
                alert("Ouch! Looks like the site is having problems");
            })
    })

    $("#signup_btn").click(function() {
        $.post( "/signup", $( "#signup_form" ).serialize() )
            .done(function(data) {
                var email = $("#signup_email").val()
                logged_in(email)
            })
            .fail(function(data) {
                data = JSON.parse(data.responseText)
                $("#signup_failed").text(data["fail"])
                $("#signup_failed").show()
            })
    })
})


function logged_out() {
    $("#logged_out_options").show()
    $("#logged_in_options").hide()
}


function logged_in(email) {
    $("#logged_out_options").hide()
    $("#logged_in_options").show()
    $("#login").hide()
    $("#signup").hide()

    if (!email)
        email = user_logged_in

    $("#logout_link").text("Log out [" + email + "]")
}
