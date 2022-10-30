var conn = null;

console.log("oops");

document.addEventListener("DOMContentLoaded", function() {
    console.log("ues");
    connect();
});

function log(msg) {
    var control = $('#log');
    control.html(control.html() + msg + '<br/>');
    control.scrollTop(control.scrollTop() + 1000);
}

function connect() {
    // разрываем соединение если функция вызвана по-ошибке
    disconnect();

    var wsUri = (window.location.protocol == 'https:' && 'wss://' || 'ws://') + window.location.host + "/ws";
    //открываем соединение
    log(wsUri);
    conn = new WebSocket(wsUri);

    log('Connecting...');
    conn.onopen = function () {
        log('Connected.');
    };
    conn.onmessage = function (e) {
        log('Received: ' + e.data);
    };
    conn.onclose = function () {
        log('Disconnected.');
        conn = null;
    };
}

function disconnect() {
    if (conn != null) {
        log('Disconnecting...');
        conn.close();
        conn = null;
    }
}