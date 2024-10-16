var form_ = $("#form_").validate({
    rules: {
        name: { required: true },
        type: { required: true },
        value: { required: true },
        active: { required: true },
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
    $("#form_ input[name='name']").focus();

    $(".btnBack").on("click", function () {
        window.location.href = '/page/repository/';
    });

    $("#form_").on("submit", function () {
        if (form_.valid()) {
            $("form input, form button").blur();
            $("#form_").LoadingOverlay("show");

            api.post('', {
                "name": $("#form_ input[name='name']").val(),
                "allocation": $("#form_ input[name='allocation']").val(),
                "datalink": $("#form_ input[name='datalink']").val(),
                "user": $("#form_ input[name='user']").val(),
                "password": $("#form_ input[name='password']").val(),
                "active": $("#form_ select[name='active']").val(),
            })
                .then(function (response) {
                    idU = response.data.id;
                    Swal.fire("Tersimpan!", "", "success")
                        .then(() => {
                            window.location.href = '/page/repository/{{clientId}}/{{sessionId}}/' + idU;
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