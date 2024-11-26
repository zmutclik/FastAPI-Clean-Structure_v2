var mnEditor = new MenuEditor('MenuEditor_', { maxLevel: 4 });
mnEditor.onClickDelete((event) => {
    let itemData = event.item.getDataset();
    Swal.fire({
        title: 'Apakah anda YAKIN ingin menghapus Menu "' + itemData.text + '"?',
        showCancelButton: true,
        confirmButtonText: "Ya HAPUS",
    }).then((result) => {
        if (result.isConfirmed) {
            api.delete('/data/' + itemData['id'])
                .then(function () {
                    Swal.fire("Terhapus!", "", "success")
                        .then(() => {
                            getMenu();
                        });
                })
        }
    });
});

mnEditor.onClickEdit((event) => {
    let itemData = event.item.getDataset();
    mnEditor.edit(event.item); // set the item in edit mode
    api.get('/data/' + itemData['id'])
        .then(function (response) {
            $('.panelSubmit').hide();
            $('#menuid').val(response.data.id);
            $('#menutext').val(response.data.text);
            $('#menutooltop').val(response.data.tooltop);
            $('#menuhref').val(response.data.href);
            $('#menuicon').val(response.data.icon);
            $('#menusegment').val(response.data.segment);
            if (response.data.disabled)
                $('#menudisabled').val('1').trigger('change');
            else
                $('#menudisabled').val('0').trigger('change');
            $('#menutext').focus();
            toggleBtn();
        })
        .catch(function (error) {
        })
        .finally(function () {
        });
});

function getMenu() {
    mnEditor.empty();
    $("#MenuEditor_").LoadingOverlay("show");
    api.get('/menus')
        .then(function (response) {
            mnEditor.setArray(response.data);
        })
        .catch(function (error) {
        })
        .finally(function () {
            mnEditor.mount();
            $("#MenuEditor_").LoadingOverlay("hide");
        });
}

function toggleBtn() {
    if ($('.panelSubmit').is(":visible")) {
        $('.panelAdd').show();
        $('.panelSubmit').hide();
        $("form input, form select").prop("disabled", true);
    } else {
        $('.panelAdd').hide();
        $('.panelSubmit').show();
        $("form input, form select").prop("disabled", false);
    }
}

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
    getMenu();
    toggleBtn();
    $(".btnBack").on("click", function () {
        window.location.href = '{{prefix_url}}/';
    });
    $("#btnAdd,.btnCancel").on("click", function () {
        toggleBtn();
        $('#menuid').val('');
        $('#menutext').val('');
        $('#menutooltop').val('');
        $('#menuhref').val('');
        $('#menuicon').val('');
        $('#menusegment').val('');
        $('#menudisabled').val('0').trigger('change');
    });

    $("#form_").on("submit", function () {
        if (form_.valid()) {
            $("form input, form button").blur();
            $("#form_").LoadingOverlay("show");
            menuid = $("#menuid").val();
            if (menuid !== '') menuid = "/" + menuid

            api.post('/data' + menuid, {
                "text": $("#form_ input[name='text']").val(),
                "tooltip": $("#form_ input[name='tooltip']").val(),
                "href": $("#form_ input[name='href']").val(),
                "type": $("#form_ input[name='type']").val(),
                "icon": $("#form_ input[name='icon']").val(),
                "segment": $("#form_ input[name='segment']").val(),
                "disabled": $("#menudisabled").val(),
            })
                .then(function (response) {
                    getMenu();
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
                    toggleBtn();
                });
        }
        return false;
    });
    $("#btnSabeSort").on("click", function () {
        let output = mnEditor.getString();
        $("#MenuEditor_").LoadingOverlay("show");
        api.post('/menus', JSON.parse(output))
            .then(function (response) {
            })
            .catch(function (error) {
            })
            .finally(() => {
                $("#MenuEditor_").LoadingOverlay("hide");
            });
    });
});