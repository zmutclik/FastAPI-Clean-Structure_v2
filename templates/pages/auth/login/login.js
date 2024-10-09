var formLogin = $("#formLogin").validate({
    rules: {
        email: { required: true },
        password: { required: true },
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
    $("#formLogin").on("submit", function () {
        if (formLogin.valid()) {
            $('#formLogin input,#formLogin button').blur();
            $("#formLogin").LoadingOverlay("show");
            axios.post('{{clientId}}/{{sessionId}}/login', { "email": $('#formLogin input[name=email]').val(), "password": $('#formLogin input[name=password]').val() })
                .then(function (response) {
                    window.location.href = "{{nextpage}}";
                })
                .catch(function (error) {
                    formLogin.showErrors({
                        "email": error.response.data.detail,
                        "password": error.response.data.detail,
                    });
                })
                .finally(() => {
                    $("#formLogin").LoadingOverlay("hide");
                });
        }
        return false;
    });

});