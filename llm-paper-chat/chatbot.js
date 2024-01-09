let fileId; // Global variable to store fileId

$(document).ready(function() {
        const urlParams = new URLSearchParams(window.location.search);
        fileId = urlParams.get('fileId');
        $('#sendButton').click(function() {
            var message = $('#messageInput').val().trim();
            if(message) {
                $('#chatWindow').append('<div class="p-2"><b>You</b><br/>' + message + '</div>');
                $('#messageInput').val('');
                chat_backend(fileId, message);
            }
        });
    
        $('#messageInput').keypress(function(e) {
            if(e.which == 13) { // Enter key pressed
                $('#sendButton').click();
            }
        });
});

function handleResponse(response) {
    response.json().then((resp) => {
        $('#chatWindow').append('<div class="p-2"><b>ChatLCA</b><br/>' + resp['content'] + '</div>');
    });
}

function chat_backend(fileId, message) {
        const formData = new FormData();
        formData.append("fileId", fileId);
        formData.append("message", message);
        return fetch(SERVER_ADDRESS + "/chat", {
                method: "POST",
                body: formData,
                mode: "cors",
        })
        .then(handleResponse)
        .catch((error) => {
                // Handle error
                console.error(error);
        });
}
