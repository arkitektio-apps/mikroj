/*
 * Particle Analyzer
 * 
 * Analyzes all particles in an image
 * 
 * @setactivein
 * @takeactiveout
 */
#@ Integer (label="Size", value=20) minSize

setAutoThreshold("Default dark no-reset");
//run("Threshold...");
setAutoThreshold("Default dark no-reset");
setOption("BlackBackground", true);
run("Convert to Mask");
run("Analyze Particles...", "size="+ minSize + "-Infinity display");
