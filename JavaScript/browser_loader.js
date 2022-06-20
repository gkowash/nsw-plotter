const load_file = function() {
  h.openRootFile(this.dataset.file);
  console.log("Opened file", this.dataset.file)
}

var file_links = document.getElementsByClassName("file");
var i;

for (i=0; i < file_links.length; i++) {
  file_links[i].addEventListener("click", load_file);
}
