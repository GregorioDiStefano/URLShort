$(window).load(function(){
    $("#enter_url").keyup(function (e) {
        if ($(this).val() == "") {
            $(".arrow_box").hide()
        }
        if (e.keyCode == 13) {
            if ($("input#enter_url").val().toLowerCase().search(/[.][a-z]+/) == -1)
                return
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



var token = "";

$(document).ready(function() {
    $("#login").hide()
    $("#login_failed").hide()
    $("#signup_failed").hide()
    $("#signup").hide()


    $("#user_table").hide()

    if (user_logged_in)
        logged_in()

    var hashVal = window.location.hash.split("#")[1];
    if(hashVal == 'reset') {
        $("#reset_passwd").show()
        $("#dim-screen").show()
        token = gup("token")
    }


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

		var d = new Date()
	        $("#inline_captcha > img").attr("src", "/captcha?"+d.getTime());
                
                $("#signup_failed").text(data["fail"])
                $("#signup_failed").show()
            })
    })

    $('#reset_btn').click( function() {
        if ($("input[name=password1]").val() != $("input[name=password2]").val()
            || $("input[name=password1]").val() == "")
        {
            alert("Passwords dont match")
        }

        else if ($("input[name=password1]").val().length < 5)
        {
            alert("Ugh, seriously? Picka longer password.")
        }

        else {
            var new_password = $("input[name=password1]").val()
            $.post( "/reset", { "new_password": new_password, "token": token })
                .fail(function( data ) {
                    //TODO: show error here
                })

                .done(function( data ) {
                    window.location = window.location.origin
                });
        }
    })

    $("#passwd_reset").click(function() {
        $.get("api?pw_reset=True&email="+$("#login_email").val())
        swal("Password reset!", "Check your e-mail to complete the password reset process", "success")
    })

})

function remove_protocol(url) {
    if (url.indexOf("https://") === 0)
        return url.substr(8)
    else if (url.indexOf("http://") == 0)
        return url.substr(7)
    else return url
}

function fill_table() {
        var jqxhr = $.get( "/api?list=json", function() {
        })
        .done(function(data) {
            var urls = data["urls"]
            urls.forEach(function(item) {
                $('#user_table tr:last').clone().appendTo("#user_table")

                $('#user_table tr:last .accessed').text(item.accessed)
                $('#user_table tr:last .url a' ).text(remove_protocol(item.url))
                $('#user_table tr:last .url a' ).attr("href", item.url)

                $('#user_table tr:last .original_url a').text(item.original_url.length > 35 
                                                        ? item.original_url.substring(0,35) + "..." + item.original_url.substr(item.original_url.length - 10) 
                                                        : item.original_url)
                $('#user_table tr:last .original_url a').attr("href", item.original_url)
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

function gup( name, url ) {
  if (!url) url = location.href
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( url );
  return results == null ? null : results[1];
}
