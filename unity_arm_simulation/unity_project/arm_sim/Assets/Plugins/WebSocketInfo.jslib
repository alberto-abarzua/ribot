mergeInto(LibraryManager.library, {
    GetWebSocketIp: function () {
        const params = new URLSearchParams(window.location.search);
        const ip = params.get("ip");

        if (ip) {
            console.log("SetWebSocketInfo: " + ip);
            var bufferSize = lengthBytesUTF8(ip) + 1;
            var buffer = _malloc(bufferSize);
            stringToUTF8(ip, buffer, bufferSize);
            return buffer;
        }
    },
    GetWebSocketPort: function () {
        const params = new URLSearchParams(window.location.search);
        const port = params.get("port");
        if (port) {
            console.log("SetWebSocketInfo: " + port);
            return port;
        }
    },
    GetWebSocketProtocol: function () {
        const params = new URLSearchParams(window.location.search);
        const protocol = params.get("protocol");
        if (protocol) {
            console.log("SetWebSocketInfo: " + protocol);
            return protocol;
        }
    },
});
