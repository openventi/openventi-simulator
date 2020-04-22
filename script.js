window.onload = function() {
    connect();
    for (i = 0; i < 3; i++) {
        var ctx = $('#canvas' + i)[0].getContext('2d');
        window.myLine.push(new Chart(ctx, config[i]));
    }
};

var ws = null;
var message_input = $('#message');
var connected = 0;
var request_id = -1;
var request_parameter = '';
var key = '12341234';

function getToken(key, msg) {
    var hash = CryptoJS.HmacSHA256(msg, key).toString(CryptoJS.enc.Hex);
    return hash;
}

function wsSend(request, id, tokenize) {
    if (request_id === -1) {
        request_id = id; //act as lock

        if (tokenize === true) {
            var json = JSON.stringify(request);
            request.token = getToken(key, json);
        }

        console.log(request);
        showMessage('Transmitiendo parámetros');
        try {
            ws.send(JSON.stringify(request));
        } catch (err) {
            request_id = -1;
            showMessage('Error de transmisión');
        }
    } else {
        showMessage('Espere a que se termine de procesar la transmisión anterior.');
    }
}

function processGraph(json) {
    var parameters = json['data'];
    var x_coord = c++;

    Object.keys(parameters).forEach(function(key, index) {
        data = config[index].data.datasets[0].data;
        data.push({ x: x_coord, y: parameters[key] });
        data.shift();
        window.myLine[index].update();
    });
    // showMessage('Stream', json, 'primary');

    $('#stream').html(JSON.stringify(json));
}

function processSensor(json) {
    sensors = json['data'];
    for (var sensor in sensors) {
        var elem = $('#sensor_' + sensor);
        if (elem !== null) {
            $(elem).html(sensors[sensor].toFixed(2));
        }
    }
}

function processConfig(json) {
    parameters = json['data'];
    showMessage('Parameters pushed', json, 'primary');
    for (var parameter in parameters) {
        $('#' + parameter).val(parameters[parameter]);
    }
}

function processAlert(json) {
    showMessage(json['message'], json, 'danger');
}

function showMessage(message, json_data, type) {
    if (json_data !== null && json_data !== undefined) {
        var jsonPretty = JSON.stringify(json_data, null, '\t');
    }

    type = type || 'primary';
    var html =
        '<div class="alert alert-dismissible alert-' + type + '">' + '<span id="message">' + message + '</span>' + '</div>';
    $(message_input).html(html);
    html =
        '<div class="card border-' +
        type +
        ' mb-3">' +
        '<div class="card-body">' +
        '<p class="card-text">' +
        '<pre id="data">' +
        jsonPretty +
        '</pre>' +
        '</p>' +
        '</div>' +
        '</div>';
    $('#data').html(html);
}

(function($) {
    $.fn.serializeFormJSON = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };
})(jQuery);

$('form').submit(function(e) {
    e.preventDefault();
    var data = $(this).serializeFormJSON();
    var model = $(this).attr('model');
    setRequest(model, data);
});

function setRequest(model, data) {
    var request = {
        id: Math.floor(Math.random() * 999999),
        action: 'set',
        data: data,
        model: model,
        ts: Date.now(),
        token: '',
    };

    wsSend(request, request.id, true);
}

function getRequest(model) {
    var request = {
        id: Math.floor(Math.random() * 999999),
        action: 'get',
        model: model,
        token: '',
    };

    wsSend(request, request.id, true);
}

function connect() {
    if (connected === 0) {
        var ip = $('#ip').val();
        var port = $('#port').val();
        WSConn(ip, port);
    } else {
        showMessage('Ya se encuentra conectado...', 1);
    }
}

function disconnect() {
    ws.close();
    connected = 0;
    showMessage('Desconectado!', '');
}

function WSConn(ip, port) {
    if ('WebSocket' in window) {
        console.log('ws://' + ip + ':' + port + '/');
        ws = new WebSocket('ws://' + ip + ':' + port + '/');

        ws.onopen = function() {
            showMessage('Conectado exitosamente!', 1);
            connected = 1;
        };

        ws.onmessage = function(evt) {
            var json = JSON.parse(evt.data);
            var data_type = json['t'];
            if (jQuery.inArray(data_type, [0, 1, 2, 3]) !== -1) {
                switch (data_type) {
                    case 0:
                        processGraph(json);
                        break;
                    case 1:
                        processAlert(json);
                        break;
                    case 2:
                        processConfig(json);
                        break;
                    case 3:
                        processSensor(json);
                        break;
                    default:
                }
            } else if (parseInt(json['id']) === request_id) {
                var message = JSON.stringify(json);
                showMessage('Request completado', json);
                console.log('Recibido: ' + message);
                request_id = -1;
            } else {
                showMessage('Trama recibida incorrecta', 1);
            }
        };

        ws.onclose = function() {
            showMessage('Desconectado!', '');
            connected = 0;
            request_parameter = '';
            request_id = -1;
        };
    } else {
        showMessage('Navegador no soporta websockets', '');
    }
}

var c = 0;

var config = [];

var data0 = [];
var data1 = [];
var data2 = [];

var options = {
    tooltips: { enabled: false },
    legend: { display: false },
    scales: {
        xAxes: [{
            type: 'linear',
            display: false,
            ticks: {
                stepSize: 1,
            },
        }, ],
        yAxes: [{
            display: true,
            ticks: {
                max: 40,
                beginAtZero: true,
            },
            gridLines: {
                color: 'dimgray',
                zeroLineColor: 'white',
                drawBorder: true,
            },
        }, ],
    },
    elements: {
        point: {
            radius: 0,
        },
    },
};
window.myLine = [];
for (var i = 0, t = 40; i < 200; i++) {
    x_coord = c++;
    data0.push({ y: 0, x: x_coord });
    data1.push({ y: 0, x: x_coord });
    data2.push({ y: 0, x: x_coord });
}

config.push({
    type: 'line',
    data: {
        datasets: [{
            data: data0,
            lineTension: 0,
            borderColor: 'yellow',
            fill: false,
        }, ],
    },
    options: options,
});

config.push({
    type: 'line',
    data: {
        datasets: [{
            data: data1,
            lineTension: 0,
            borderColor: 'lightgreen',
        }, ],
    },
    options: options,
});

config.push({
    type: 'line',
    data: {
        datasets: [{
            data: data2,
            lineTension: 0,
            borderColor: 'white',
        }, ],
    },
    options: options,
});