// Sliders and scroll bars
#@ Double (value=1, min=0, max=10, stepSize=0.001, persist=false, style=slider) m
#@ Double (value=1, min=0, max=10, stepSize=0.001, persist=false, style="slider,format:0.0000") n
#@ String (label="Please enter your name") name
#@ output String greeting
#@ Integer (label="An integer!",value=15) someInt`
#@ Integer (label="An integer!", value=15, persist=false) someInt`
#@ String (visibility=MESSAGE, value="This is a documentation line", required=false) msg
#@ Integer (label="Some integer parameter") my_int
#@ String (visibility=MESSAGE, value="<html>Message line 1<br/>Message line 2<p>Let's make a list<ul><li>item a</li><li>item b</li></ul></html>") docmsg
#@ Integer anIntParam
#@ String (choices={"Option 1", "Option 2"}, style="listBox") myChoice123
#@ String (choices={"Option A", "Option B"}, style="radioButtonHorizontal") myChoiceABC
#@ File (label="Select a file") myFile
#@ File[] listOfPaths (label="select files or folders", style="both")
#@ File (label="Select a file", style="file") myFile
#@ File (label="Select a directory", style="directory") myDir
#@ File[] (label="Select some files", style="files") listfiles
#@ File[] (label="Select some directories", style="directories") listdirs