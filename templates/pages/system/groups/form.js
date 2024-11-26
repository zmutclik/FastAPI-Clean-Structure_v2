var form_ = $("#form_").validate({
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
    $("#form_ input[name='group']").focus();

    $('#jstree_').jstree({
        'core': {
            'data': {
                'url': function (node) {
                    return 'menu/' + $('#menutype_id').val() + '/{{group}}';
                }
            }
        }, "plugins": ["checkbox"]
    });

    $('#menutype_id').on('change', function () {
        $('#jstree_').jstree(true).destroy();

        $('#jstree_').jstree({
            'core': {
                'data': {
                    'url': function (node) {
                        return 'menu/' + $('#menutype_id').val() + '/{{group}}';
                    }
                }
            }, "plugins": ["checkbox"]
        });


    });

    $(".btnBack").on("click", function () {
        window.location.href = '{{prefix_url}}/';
    });

    $("#form_").on("submit", function () {
        if (form_.valid()) {
            $("form input, form button").blur();
            $("#form_").LoadingOverlay("show");

            api.post('', {
                "group": $("#form_ input[name='group']").val(),
                "desc": $("#form_ input[name='desc']").val(),
                "menutype_id": $("#menutype_id").val(),
                "menu": $('#jstree_').jstree('get_selected'),
            })
                .then(function (response) {
                    idU = response.data.id;
                    Swal.fire("Tersimpan!", "", "success")
                        .then(() => {
                            window.location.href = '{{prefix_url}}/{{clientId}}/{{sessionId}}/' + idU;
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