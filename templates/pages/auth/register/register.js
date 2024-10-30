var form_ = $("#form_").validate({
    rules: {
        username: { required: true },
        full_name: { required: true },
        email: { required: true, email: true },
        password: { required: true },
        password2: { required: true },
    },
    errorElement: 'div',
    errorPlacement: function (error, element) {
        error.addClass('invalid-feedback');
        element.next().after(error);
    },
    highlight: function (element, errorClass, validClass) {
        $(element).addClass('is-invalid');
    },
    unhighlight: function (element, errorClass, validClass) {
        $(element).removeClass('is-invalid');
    },
});
function check(n, m) {
    if (n < 6) {
        percentage = 0;
        $(".progress-bar").css("background", "#dd4b39");
    } else if (n < 8) {
        percentage = 20;
        $(".progress-bar").css("background", "#9c27b0");
    } else if (n < 10) {
        percentage = 40;
        $(".progress-bar").css("background", "#ff9800");
    } else {
        percentage = 60;
        $(".progress-bar").css("background", "#4caf50");
    }
    // Check for the character-set constraints 
    // and update percentage variable as needed. 
    //Lowercase Words only 
    if ((m.match(/[a-z]/) != null)) {
        percentage += 10;
    }
    //Uppercase Words only 
    if ((m.match(/[A-Z]/) != null)) {
        percentage += 10;
    }
    //Digits only 
    if ((m.match(/0|1|2|3|4|5|6|7|8|9/) != null)) {
        percentage += 10;
    }
    //Special characters 
    if ((m.match(/\W/) != null) && (m.match(/\D/) != null)) {
        percentage += 10;
    }
    // Update the width of the progress bar 
    $(".progress-bar").css("width", percentage + "%");
    $(".progress-bar").html(percentage + "%");
}

$(document).ready(function () {
    $("#password").keyup(function () {
        var m = $(this).val();
        var n = m.length;
        // Function for checking 
        check(n, m);
    });

    $("#form_").on("submit", function () {
        if (form_.valid()) {
            if ($('#form_ input[name=password]').val() != $('#form_ input[name=password2]').val()) {
                form_.showErrors({ "password": "Password tidak sama.!", "password2": "Password tidak sama.!" });
            } else if (percentage <= 70) {
                form_.showErrors({ "password": "Mohon kombinasi PASSWORD bernilai minimal 70%. !" });
            } else {
                $('#form_ input,#formLogin button').blur();
                $("#form_").LoadingOverlay("show");
                dataIn = {
                    "username": $('#form_ input[name=username]').val(),
                    "full_name": $('#form_ input[name=full_name]').val(),
                    "email": $('#form_ input[name=email]').val(),
                    "password": $('#form_ input[name=password]').val(),
                    "password2": $('#form_ input[name=password2]').val(),
                }
                axios.post('{{clientId}}/{{sessionId}}/register', dataIn)
                    .then(function (response) {
                        Swal.fire({
                            icon: "success",
                            title: "Akun anda Sudah berhasil terdaftar.!",
                            showConfirmButton: false,
                            timer: 2000
                        }).then(() => {
                            window.location.href = '/auth/login';
                        });
                    })
                    .catch(function (error) {
                        if (error.status == 401 || error.status == 400) {
                            Swal.fire({
                                position: "top-end",
                                icon: "error",
                                title: error.response.data.detail,
                                showConfirmButton: false,
                                timer: 2000
                            }).then((result) => {
                                if (error.response.data.detail.includes("Session"))
                                    window.location.reload(true);
                            });
                        }
                        if (error.status == 422) {
                            de = {}
                            $.each(error.response.data.detail, function (i, v) {
                                de[v.loc[1]] = v["msg"];
                            });
                            formLogin.showErrors(de);
                        }
                    })
                    .finally(() => {
                        $("#form_").LoadingOverlay("hide");
                    });
            }
        }
        return false;
    });

});