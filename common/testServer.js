 /* Load the HTTP library */
  var http = require("http");

  /* Create an HTTP server to handle responses */

  http.createServer(function(request, response) {
    response.writeHead(200, {"Content-Type": "text/plain"});
    response.write("Spotify Lyricist Test Echo Server");
    //response.write(request);
    response.end();
  }).listen(8080);