var percentage = 0;
var form_gantipassword = $("#form_gantipassword").validate({
    errorElement: 'div',
    errorPlacement: function (error, element) {
        error.addClass('invalid-feedback');
        element.after(error);
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
    $("#password_baru").keyup(function () {
        var m = $(this).val();
        var n = m.length;
        // Function for checking 
        check(n, m);
    });


    $("#form_gantipassword").on("submit", function () {
        if (form_gantipassword.valid()) {
            if (percentage <= 70) {
                form_gantipassword.showErrors({ "baru": "Mohon kombinasi PASSWORD bernilai minimal 70%. !" });
            } else if ($("#form_gantipassword input[name='lama']").val() == $("#form_gantipassword input[name='baru']").val()) {
                form_gantipassword.showErrors({ "baru": "Password tidak boleh sama dengan yg lama." });
            } else {
                $("form input, form button").blur();
                $("#form_gantipassword").LoadingOverlay("show");
                api.post('/gantipassword/{{id}}', {
                    "lama": $("#form_gantipassword input[name='lama']").val(),
                    "baru": $("#form_gantipassword input[name='baru']").val(),
                })
                    .then(function (response) {
                        Swal.fire("Tersimpan!", "", "success");
                    })
                    .catch(function (error) {
                        if (error.status == 401 || error.status == 400) {
                            Swal.fire({
                                position: "top-end",
                                icon: "error",
                                title: error.response.data.detail,
                                showConfirmButton: false,
                                timer: 2000
                            });
                        }
                        if (error.status == 422) {
                            de = {}
                            $.each(error.response.data.detail, function (i, v) {
                                de[v.loc[1]] = v["msg"];
                            });
                            form_setting.showErrors(de);
                        }
                    })
                    .finally(() => {
                        $("#form_gantipassword").LoadingOverlay("hide");
                    });
            }
        }
        return false;
    });
});