// Add click event listeners to file tree menu

var toggler = document.getElementsByClassName("caret");
var i;

for (i = 0; i < toggler.length; i++) {
  toggler[i].addEventListener("click", function() {
    this.parentElement.querySelector(".nested").classList.toggle("active");
    this.classList.toggle("caret-down");
  });
}


// Highlight currently active tab on nav bar

var url = window.location.href;

$(".nav a").each(function() {
  console.log('URL ', url);
  console.log('THIS', this.href);
  // finds nav tab for current window; ".nav a.active" is modified in style.css
  if (url == this.href) {
    $(this).addClass("active");
  }
});


/*
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
  });
}

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;

  });
}
*/
