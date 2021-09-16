var table;

function insertTrack(trackData) {
    let trackRow = table.insertRow();
    artistColumn = trackRow.insertCell();
    trackColumn = trackRow.insertCell();
    albumCoverColumn = trackRow.insertCell();
    previewColumn = trackRow.insertCell();

    artistColumn.innerHTML = trackData.artist;
    trackColumn.innerHTML = trackData.track;

    let imgElement = document.createElement("img");
    imgElement.src = trackData.album_image_url;
    albumCoverColumn.appendChild(imgElement);
    
    let linkElement = document.createElement("a");
    linkElement.innerHTML = 'Preview';
    linkElement.setAttribute('href', trackData.preview_url);
    previewColumn.appendChild(linkElement);
    
}

function fillTable() {
    let genre = document.getElementById('genre').value;
    table.textContent = "";

    fetch('http://localhost:5000/tracks/' + encodeURI(genre))
        .then(response => response.json())
        .then(data => {
            data.forEach(element => {
                insertTrack(element);
            });
        }).catch(err => {
            alert("Specified Genre Is Not Found");
        })
}

document.addEventListener("DOMContentLoaded", function(){
    table = document.getElementById("trackTable");
});