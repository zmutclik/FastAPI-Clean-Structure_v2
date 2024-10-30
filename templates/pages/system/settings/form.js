var form_setting = $("#form_setting").validate({
    rules: {
        APP_NAME: { required: true },
        APP_DESCRIPTION: { required: true },
        CLIENTID_KEY: { required: true },
        SESSION_KEY: { required: true },
        TOKEN_KEY: { required: true },
        TOKEN_EXPIRED: { required: true, number: true },
        SECRET_TEXT: { required: true },
        ALGORITHM: { required: true },
    },
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
$(document).ready(function () {
    $("#form_setting").on("submit", function () {

        if (form_setting.valid()) {
            $("form input, form button").blur();
            $("#form_setting").LoadingOverlay("show");

            api.post('', {
                "APP_NAME": $("#form_setting input[name='APP_NAME']").val(),
                "APP_DESCRIPTION": $("#form_setting input[name='APP_DESCRIPTION']").val(),
                "CLIENTID_KEY": $("#form_setting input[name='CLIENTID_KEY']").val(),
                "SESSION_KEY": $("#form_setting input[name='SESSION_KEY']").val(),
                "TOKEN_KEY": $("#form_setting input[name='TOKEN_KEY']").val(),
                "TOKEN_EXPIRED": $("#form_setting input[name='TOKEN_EXPIRED']").val(),
                "SECRET_TEXT": $("#form_setting input[name='SECRET_TEXT']").val(),
                "ALGORITHM": $("#form_setting input[name='ALGORITHM']").val(),
            })
                .then(function (response) {
                    Swal.fire("Tersimpan!", "", "success")
                        .then((result) => {
                            Swal.fire({
                                text: "Mohon Restart System untuk mendapatkan Pengaruh Perubahan.",
                                icon: "error"
                            });
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
                        });
                    } else if (error.status == 422) {
                        de = {}
                        $.each(error.response.data.detail, function (i, v) {
                            de[v.loc[1]] = v["msg"];
                        });
                        form_setting.showErrors(de);
                    } else if (error.status == 500) {
                        Swal.fire({
                            position: "top-end",
                            icon: "error",
                            title: "Error pada system, Mohon hubungi Support System anda...",
                            showConfirmButton: false,
                            timer: 2000
                        });
                    }
                })
                .finally(() => {
                    $("#form_setting").LoadingOverlay("hide");
                });
        }
        return false;
    });
});