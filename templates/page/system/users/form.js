var form_ = $("#form_").validate({
    rules: {
        full_name: { required: true },
        username: { required: true },
        email: {
            required: true,
            email: true,
        },
        limit_expires: { number: true },
    },
    errorElement: 'span',
    errorPlacement: function (error, element) {
        error.addClass('invalid-feedback');
        element.closest('.input-group').append(error);
    },
    highlight: function (element, errorClass, validClass) {
        $(element).addClass('is-invalid');
    },
    unhighlight: function (element, errorClass, validClass) {
        $(element).removeClass('is-invalid');
    },
});
$(document).ready(function () {
    $("#form_ input[name='full_name']").focus();

    $(".btnBack").on("click", function () {
        window.location.href = '/page/users/';
    });

    $("#form_").on("submit", function () {
        if (form_.valid()) {
            $("form input, form button").blur();
            $("#form_").LoadingOverlay("show");

            api.post('', {
                "full_name": $("#form_ input[name='full_name']").val(),
                "username": $("#form_ input[name='username']").val(),
                "email": $("#form_ input[name='email']").val(),
                "limit_expires": $("#form_ input[name='limit_expires']").val(),
            })
                .then(function (response) {
                })
                .catch(function (error) {
                    console.log(error);
                    if (error.status == 401) {
                        Swal.fire({
                            position: "top-end",
                            icon: "error",
                            title: error.response.data.detail,
                            showConfirmButton: false,
                            timer: 2000
                        });
                    }

                    form_.showErrors({
                        "full_name": "",
                        "username": "",
                        "email": "",
                        "limit_expires": "",
                    });
                })
                .finally(() => {
                    $("#form_").LoadingOverlay("hide");
                });
        }
        return false;
    });
});