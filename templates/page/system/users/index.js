$(document).ready(function () {
    $('#table_').DataTable({
        serverSide: true,
        ajax: {
            "url": '/page/users/{{clientId}}/{{sessionId}}/datatables', "contentType": "application/json", "type": "POST",
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
            { "data": "username", "title": "USERNAME", },
            { "data": "email", "title": "EMAIL", },
            { "data": "full_name", "title": "NAMA", },

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
        window.location.href = '/page/users/{{clientId}}/{{sessionId}}/add';
    });

    $("#table_").on("click", '.btnEdit', function () {
        window.location.href = '/page/users/{{clientId}}/{{sessionId}}/' + $(this).parents('tr').attr('id');
    });
});