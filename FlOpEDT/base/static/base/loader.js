/*----------------------
   ------ LOADER -------
  ----------------------*/

var cpt_loader = 0;

// show/hide le div 'loader' and count method's call
// the loader is hide only if cpt_loader==0
function show_loader(doit) {
    if (doit) {
        cpt_loader ++;
        $('#loader').css("visibility", "visible");
    } else {
        cpt_loader --;
        if (cpt_loader<=0) {
            cpt_loader=0;
            $('#loader').css("visibility", "hidden");
        }
    }
    //console.log('loader : '+doit+' cpt='+cpt_loader);
}
