const load_file = function() {
  h.openRootFile(this.data-file);
  console.log("Opened file", this.data-file)
}

var file_links = document.getElementsByClassName("file");
var i;

for (i=0; i < file_links.length; i++) {
  file_links[i].addEventListener("click", load_file);
}
