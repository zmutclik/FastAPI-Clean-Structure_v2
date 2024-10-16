
var oTable;
$(document).ready(function () {
    oTable = $('#table_').DataTable({
        serverSide: true,
        ajax: {
            "url": '/page/repository/{{clientId}}/{{sessionId}}/datatables', "contentType": "application/json", "type": "POST",
            "data": function (d) {
                return JSON.stringify(d);
            }
        },
        "paging": false,
        "lengthChange": false,
        "searching": false,
        "ordering": true,
        "info": false,
        "autoWidth": false,
        "responsive": true,
        columns: [
            { "data": "name", "title": "NAMA", },
            { "data": "allocation", "title": "PERUNTUKAN", },
            { "data": "datalink", "title": "DATALINK", },
            { "data": "user", "title": "USER", },
            { "data": "active", "title": "AKTIF", },
            { "data": "id", "title": "" },
        ],
        columnDefs: [{
            sClass: "right", searchable: false, orderable: false, bSortable: false, targets: -1, sWidth: "0px",
            render: function (data, type, row, meta) {
                btnhtml = "<div class=\"btn-group\" role=\"group\">";
                btnhtml += "<button type=\"button\" class=\"btn btn-success btnEdit\"><i class=\"lni lni-pencil-alt\"></i></button>";
                btnhtml += "<button type=\"button\" class=\"btn btn-danger btnDelete\"><i class=\"lni lni-trash-can\"></i></button>";
                btnhtml += "</div>"
                return btnhtml;
            }
        }],
    });

    $("#btnTambah").on("click", function () {
        window.location.href = '/page/repository/{{clientId}}/{{sessionId}}/add';
    });

    $("#table_").on("click", '.btnEdit', function () {
        window.location.href = '/page/repository/{{clientId}}/{{sessionId}}/' + $(this).parents('tr').attr('id');
    });

    $("#table_").on("click", '.btnDelete', function () {
        var nm = $(this).parents('tr').find("td:nth-child(1)").html();
        var idU = $(this).parents('tr').attr('id');
        Swal.fire({
            title: 'Apakah anda YAKIN ingin menghapus REPOSITORY "' + nm + '"?',
            showCancelButton: true,
            confirmButtonText: "Ya HAPUS",
        }).then((result) => {
            if (result.isConfirmed) {
                api.delete(idU)
                    .then(function () {
                        Swal.fire("Terhapus!", "", "success")
                            .then(() => {
                                oTable.ajax.reload();
                            });
                    })
            }
        });
    });
});