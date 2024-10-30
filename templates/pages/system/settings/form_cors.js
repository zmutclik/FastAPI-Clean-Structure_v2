var form_cors = $("#form_cors").validate({
    rules: {
        link: {
            required: true
        }
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
    $("#form_cors").on("submit", function () {
        if (form_cors.valid()) {
            $("form input, form button").blur();
            $("#form_cors").LoadingOverlay("show");

            api.post('/cors', {
                "link": $("#form_cors input[name='link']").val(),
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
                        form_cors.showErrors(de);
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
                    oTableCors.ajax.reload();
                    $("#form_cors").LoadingOverlay("hide");
                });
        }
        return false;
    });
});