var formLogin = $("#formLogin").validate({
    rules: {
        email: { required: true },
        password: { required: true },
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

$(document).ready(function () {
    $("#formLogin").on("submit", function () {
        if (formLogin.valid()) {
            $('#formLogin input,#formLogin button').blur();
            $("#formLogin").LoadingOverlay("show");
            axios.post('{{clientId}}/{{sessionId}}/login', { "email": $('#formLogin input[name=email]').val(), "password": $('#formLogin input[name=password]').val() })
                .then(function (response) {
                    window.location.href = "{{nextpage}}";
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
                    $("#formLogin").LoadingOverlay("hide");
                });
        }
        return false;
    });

});