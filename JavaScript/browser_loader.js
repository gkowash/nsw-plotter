function load_file(file) {
  //h.openRootFile(this.dataset.file);
  h.openRootFile(file);
  console.log("Opened file ", file);
  //console.log("Opened file", this.dataset.file)
}

function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.dataset.file);
}

function drop(ev) {
  ev.preventDefault();
  var file = ev.dataTransfer.getData("text");
  load_file(file);
}

var file_links = document.getElementsByClassName("file");
var i;
for (i=0; i < file_links.length; i++) {
  //file_links[i].addEventListener("click", load_file);
  file_links[i].setAttribute("draggable", true);
  file_links[i].setAttribute("ondragstart", "drag(event)");
}

var browser = document.getElementById("simpleGUI");
browser.setAttribute("ondrop", "drop(event)");
browser.setAttribute("ondragover", "allowDrop(event)");
