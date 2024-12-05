Dropzone.autoDiscover = false;

function init() {
    let dz = new Dropzone("#dropzone", {
        url: "http://127.0.0.1:8000/upload_pdf/", // Updated URL for FastAPI server endpoint
        maxFiles: 1, // Maximum number of files allowed
        maxFilesize: 20, // Maximum file size in MB
        acceptedFiles: "application/pdf", // Accepted file types
        addRemoveLinks: true,
        dictDefaultMessage: "Drag and drop a file here or click to upload",
        autoProcessQueue: false
    });

    dz.on("addedfile", function() {
        console.log('File added:', dz.files[0].name);
        if (dz.files.length > 1) {
            dz.removeFile(dz.files[0]);
        }
    });

    dz.on("complete", function(file) {
        dz.removeFile(file);
    });

    dz.on("success", function(file, response) {
        console.log('Response from server:', response);
        if (response.error) {
            $("#error").show().html("Error: " + response.error);
        }
    });

    $("#submitBtn").on('click', function(e) {
        e.preventDefault();
        dz.processQueue();
    });
}

document.addEventListener("DOMContentLoaded", function() {
    console.log("Ready!");
    $("#error").hide();
    init();
});
