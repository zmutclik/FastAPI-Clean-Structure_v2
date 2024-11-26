
var oTable;
$(document).ready(function () {
    $('#time_end').val(moment().subtract(-10, 'minutes').format("DD MMM YYYY HH:mm"));
    $('#time_start').val(moment().subtract(6, 'hours').format("DD MMM YYYY HH:mm"));

    oTable = $('#table_').DataTable({
        serverSide: true,
        ajax: {
            "url": '{{prefix_url}}/{{clientId}}/{{sessionId}}/datatables', "contentType": "application/json", "type": "POST",
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
        "paging": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": false,
        "autoWidth": true,
        "responsive": true,
        columns: [
            { "data": "id", "title": "NO", },
            {
                "data": function (source, type, val) {
                    return moment(source.startTime, "YYYY-MM-DDTHH:mm:ss").format("YYYY-MM-DD HH:mm:ss");
                }
                , "title": "WAKTU",
            },
            {
                "data": function (source, type, val) {
                    return "<div class=\"row\"><div class=\"col\">" + source.platform + "</div></div><div class=\"row\"><div class=\"col\">" + source.browser + "</div></div>";
                }, "title": "PLATFORM",
            },
            { "data": "path", "title": "PATH", },
            {
                "data": function (source, type, val) {
                    return "<div class=\"row\"><div class=\"col\">" + source.method + "</div></div><div class=\"row\"><div class=\"col\">" + source.ipaddress + "</div></div>";
                }, "title": "IP",
            },
            { "data": "username", "title": "USERS", },
            { "data": "status_code", "title": "CODE", },
            {
                "data": function (source, type, val) {
                    return source.process_time.toFixed(3);
                }, "title": "TIME",
            },
        ],
        columnDefs: [
            {
                render: function (data, type, full, meta) {
                    return "<div class='text-wrap width-200'>" + data + "</div>";
                },
                targets: 5
            }
        ]
    });

    $("#time_start,#time_end").flatpickr({
        enableTime: true,
        dateFormat: "d M Y H:i",
        time_24hr: true, onChange: function (selectedDates, dateStr, instance) {
            oTable.ajax.reload();
        }
    });

    $("#method,#status").on("change", function (e) {
        oTable.ajax.reload();
    });

    var timer, delay = 500;
    $('#ipaddress,#querypath,#queryparam').bind('keydown blur change', function (e) {
        var _this = $(this);
        clearTimeout(timer);
        timer = setTimeout(function () {
            oTable.ajax.reload();
        }, delay);
    });


    $('.card-header').on('click', '.btnreload', function () {
        oTable.ajax.reload();
    });

    $('.card-body').on('click', '.btntimenow', function () {
        $('#time_end').val(moment().subtract(-10, 'minutes').format("DD MMM YYYY HH:mm"));
        $('#time_start').val(moment().subtract(6, 'hours').format("DD MMM YYYY HH:mm"));
        setTimeout(function () {
            oTable.ajax.reload();
        }, 200);
    });
});