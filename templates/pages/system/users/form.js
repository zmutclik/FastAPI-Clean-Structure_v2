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
                "userScopes": $('input[name="userScopes"]:checked').map(function () {
                    return $(this).val();
                }).get(),
            })
                .then(function (response) {
                    idU = response.data.id;
                    console.log(response);
                    
                    Swal.fire("Tersimpan!", "", "success")
                        .then(() => {
                            window.location.href = '/page/users/{{clientId}}/{{sessionId}}/' + idU;
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
                    }
                    if (error.status == 422) {
                        de = {}
                        $.each(error.response.data.detail, function (i, v) {
                            de[v.loc[1]] = v["msg"];
                        });
                        form_.showErrors(de);
                    }
                })
                .finally(() => {
                    $("#form_").LoadingOverlay("hide");
                });
        }
        return false;
    });
});