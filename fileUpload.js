function uploadFile(file) {
  var formData = new FormData();
  formData.append("file", file);

  return fetch("http://localhost:5000/upload", {
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

function formSubmit() {
  var fileInput = document.getElementById("fileInput");
  var file = fileInput.files[0];
  if (file) {
    uploadFile(file);
    return;
  }

  var fileId = document.getElementById("fileIdInput").value;
  if (fileId == "") {
    alert("Please select a file or enter a file id");
    return;
  }

  var formData = new FormData();
  formData.append("fileId", fileId);

  fetch("http://localhost:5000/resume", {
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

function handleResponse(response) {
  response.json().then((resp) => {
    window.location.href = "chatbot.html?fileId=" + resp.fileId;
  });
}

$("#fileInput").change(function () {
  $("#fileName").text(this.files[0].name);
  $("#fileIdInputLabel").hide();
  $("#fileIdInput").hide();
});
