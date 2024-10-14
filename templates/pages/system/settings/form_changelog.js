var form_changelog = $("#form_changelog").validate({
    rules: {
        version: { required: true },
        version_name: { required: true },
        description: { required: true },
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
    $("#form_changelog .submit").on("click", function () {

        if (form_changelog.valid()) {
            $("form input, form button").blur();
            $("#form_changelog").LoadingOverlay("show");

            api.post('/changelog', {
                "version": $("#form_changelog input[name='version']").val(),
                "version_name": $("#form_changelog input[name='version_name']").val(),
                "description": $("#form_changelog input[name='description']").val(),
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
                    }
                    if (error.status == 422) {
                        de = {}
                        $.each(error.response.data.detail, function (i, v) {
                            de[v.loc[1]] = v["msg"];
                        });
                        form_changelog.showErrors(de);
                    }
                })
                .finally(() => {
                    oTable.ajax.reload();
                    $("#form_changelog").LoadingOverlay("hide");
                });
        }
        return false;
    });
});