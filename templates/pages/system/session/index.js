
var oTable;
$(document).ready(function () {
    oTable = $('#table_').DataTable({
        serverSide: true,
        ajax: {
            "url": '{{prefix_url}}/{{clientId}}/{{sessionId}}/1/datatables', "contentType": "application/json", "type": "POST",
            "data": function (d) {
                d.search.time_start = moment($('#time_start').val(), "DD MMM YYYY HH:mm").format("YYYY-MM-DD HH:mm:ss");
                d.search.time_end = moment($('#time_end').val(), "DD MMM YYYY HH:mm").format("YYYY-MM-DD HH:mm:ss");
                d.search.ipaddress = $('#ipaddress').val();
                d.search.method = $('#method').val();
                d.search.status = $('#status').val();
                d.search.path = $('#querypath').val();
                d.search.params = $('#queryparams').val();
                return JSON.stringify(d);
            }, 'beforeSend': function (request) { request.setRequestHeader("Authorization", api.defaults.headers['Authorization']); }

        },
        "paging": false,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": false,
        "autoWidth": true,
        "responsive": true,
        columns: [
            {
                "data": function (source, type, val) {
                    typeses = "<div class=\"row\"><div class=\"col\"><strong>" + source.type + "</strong></div></div>";
                    if (source.type == 'page') typeses = "";
                    return "<div class=\"row\"><div class=\"col\">" + source.session_id + "</div></div>" + typeses;
                }, "title": "TIME",
            },
            { "data": "username", "title": "USER", },
            { "data": "platform", "title": "PLATFORM", },
            { "data": "browser", "title": "BROWSER", },
            {
                "data": function (source, type, val) {
                    return "<div class=\"row\"><div class=\"col\">start : " + moment(source.startTime, "YYYY-MM-DDTHH:mm:ss").format("YYYY-MM-DD HH:mm") + "</div></div><div class=\"row\"><div class=\"col\"> end : " + moment(source.EndTime, "YYYY-MM-DDTHH:mm:ss").format("YYYY-MM-DD HH:mm") + "</div></div>";
                }, "title": "TIME",
            },
            { "data": "LastPage", "title": "LASTPAGE", },
            { "data": "ipaddress", "title": "IPADDRESS", },
            { "data": "active", "title": "STATUS", },
            { "data": "id", "title": "" },
        ],
        columnDefs: [{
            sClass: "right", searchable: false, orderable: false, bSortable: false, targets: -1, sWidth: "0px",
            render: function (data, type, row, meta) {
                btndis = ""
                if (!row.active) btndis = " disabled"

                btnhtml = "<div class=\"btn-group\" role=\"group\">";
                btnhtml += "<button type=\"button\" class=\"btn btn-danger btnDelete\" " + btndis + "><i class=\"fas fas fa-skull\"></i></button>";
                btnhtml += "</div>"
                return btnhtml;
            }
        }],
    });


    $("#table_").on("click", '.btnDelete', function () {
        var nm = $(this).parents('tr').find("td:nth-child(2)").html();
        var idU = $(this).parents('tr').attr('id');
        Swal.fire({
            title: 'Apakah anda YAKIN ingin Membunuh Session punya "' + nm + '" ?',
            showCancelButton: true,
            confirmButtonText: "Ya KILL",
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