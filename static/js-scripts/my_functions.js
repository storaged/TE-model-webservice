function showDIV(actiondiv) {
   var foo = document.getElementById(actiondiv);

   if(foo.style.display == '' || foo.style.display == 'none'){
        foo.style.display = 'block';
   }
   else {
        foo.style.display = 'none';
   }
};

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});
