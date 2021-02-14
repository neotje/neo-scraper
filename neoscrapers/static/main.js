console.log("it do be working");

var xhttp = new XMLHttpRequest();
xhttp.open("POST", "/user/login", true)
xhttp.setRequestHeader("email", "neo@hopjes.net")
xhttp.setRequestHeader("password", "Neoscraper!")
xhttp.send()


const socket = new WebSocket('ws://0.0.0.0:9123/ws')

// Connection opened
socket.addEventListener('open', function (event) {
    socket.send('Hello Server!');
});

// Listen for messages
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});


var xhttp = new XMLHttpRequest();
xhttp.open("POST", "/scrapers/start", true)
xhttp.setRequestHeader("scraper_name", "jumbo")
xhttp.send()
