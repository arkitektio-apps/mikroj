/*
 * Particle Analyzer
 * 
 * Analyzes all particles in an image
 * 
 * @setactivein
 * @donecloseactive
 * @getresults
 */

setAutoThreshold("Default dark no-reset");
//run("Threshold...");
setAutoThreshold("Default dark no-reset");
setOption("BlackBackground", true);
run("Convert to Mask");
run("Analyze Particles...", "size=20-Infinity display");
