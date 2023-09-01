/*
 * Autothreshold
 * 
 * Run an autothreshold on the image
 * 
 * 
 * @setactivein
 * @takeactiveout
 * @donecloseactive
 */

setAutoThreshold("Default dark no-reset");
setOption("BlackBackground", true);
run("Convert to Mask");
newimgID = getImageID();
selectImage(newimgID);
