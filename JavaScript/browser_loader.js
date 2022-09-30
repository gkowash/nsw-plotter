function load_file() {
  h.openRootFile(this.dataset.file);
  console.log("Opened file", this.dataset.file)
}

function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("file", ev.target["data-file"]);
}

function drop(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("file");
  load_file(data);
}

var file_links = document.getElementsByClassName("file");
var i;
for (i=0; i < file_links.length; i++) {
  //file_links[i].addEventListener("click", load_file);
  file_links[i].setAtribute("draggable", true);
  file_links[i].setAtribute("ondragstart", drag(event));
}

var browser = document.getElementById("simpleGUI");
browser.setAtribute("ondrop", drop(event));
browser.setAtribute("ondragover", allowDrop(event));
