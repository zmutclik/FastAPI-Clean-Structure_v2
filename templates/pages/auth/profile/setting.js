var form_setting = $("#form_setting").validate({
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
            api.post('/setting/{{id}}', {
                "username": $("#form_setting input[name='username']").val(),
                "full_name": $("#form_setting input[name='full_name']").val(),
                "email": $("#form_setting input[name='email']").val(),
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
                    $("#form_setting").LoadingOverlay("hide");
                });
        }
        return false;
    });

});