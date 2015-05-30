$(window).load(function(){
    $("#enter_url").keyup(function (e) {
        if ($(this).val() == "") {
            $(".arrow_box").hide()
        }
        if (e.keyCode == 13) {
            var jqxhr = $.get( "/api?url=" + $("input#enter_url").val(), function() {
            })
            .done(function(data) {
                $(".arrow_box").show()
                $("#url").text(data["url"]);
                reset_table()
                fill_table()
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



var user_table_org = $("#user_table").clone(true);

$(document).ready(function() {
    $("#login").hide()
    $("#login_failed").hide()
    $("#signup_failed").hide()
    $("#signup").hide()


    $("#user_table").hide()

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

function fill_table() {
        var jqxhr = $.get( "/api?list=json", function() {
        })
        .done(function(data) {
            var urls = data["urls"]
            urls.forEach(function(item) {
                $('#user_table tr:last').clone().appendTo("#user_table")
                console.log("adding!")
                $('#user_table tr:last .accessed').text(item.accessed)
                $('#user_table tr:last .url').text(item.url)
                $('#user_table tr:last .original_url').text(item.original_url.length > 50 ? item.original_url.substring(0,50) + "..." : item.original_url)
                $('#user_table tr:last .date').text(item.created)
            })
        })
        .fail(function() {
        })
        .always(function() {
        });
}

function reset_table() {

   $("#user_table").find("tr:gt(1)").remove();

}

function logged_out() {
    $("#logged_out_options").show()
    $("#logged_in_options").hide()
    $("#user_table").hide()
    $("#enter_url").val("")
    $(".arrow_box").hide()
}


function logged_in(email) {
    $("#logged_out_options").hide()
    $("#logged_in_options").show()
    $("#login").hide()
    $("#signup").hide()

    if (!email)
        email = user_logged_in

    reset_table()
    fill_table()
    $("#user_table").show()
    $("#logout_link").text("Log out [" + email + "]")
}
