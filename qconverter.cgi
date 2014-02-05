#!/usr/bin/perl
#!c:/perl/bin/Perl.exe

## ##################################################################################################
##  Filename:   qconverter.cgi
##  Descripton: This tool creates a QTI XML file for each single-section WebCT quiz. 
##              It also converts the quizzes from Word Doc (as long as the questions 
##              are formatted in the required way). Right now, it's been tested to work 
##              with multiple choice, true and false, and fill in blank questions in English 
##              and Spanish. It works in Firefox, IE, and Safari. However, if there are images, 
##              you will have to upload those images later in the Sakai quizzes one by one.
##
## 
##  Author: Shawn Than   <shawn.than@cmc.edu>        
##          Melissa Zhuo <melissa.Zhuo@cmc.edu>
##
##  Copyright (c) <2006> Claremont McKenna College
##  Licensed under the Educational Community License version 1.0. 
##  For details go to http://opensource.org/licenses/ecl1.php
##
##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
##  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
##  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
##  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
##  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##           
###########################################################################################################

print "Content-Type: text/html\n\n";
print <<EOF;

<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Sakai Quiz Converter</title>
<style type="text/css">
<!--
.style1 {
	font-family: Verdana, Arial, Helvetica, sans-serif;
	font-weight: bold;
	font-size: 14px;
}
.style15 {font-size: 12px; font-family: Verdana, Arial, Helvetica, sans-serif;}
.style16 {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px; }
.style17 {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9px; font-weight: bold; }
.style18 {color: #FF0000}
.style22 {color: #FF6600}
.style23 {color: #006600}
.style25 {color: #0000FF}
.style26 {color: #000000}
.style27 {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9px; color: #006600; }
.style28 {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9px; color: #FF6600; }
-->
</style>
</head>

<body text=#000000 link="#000099" vlink="#000099" topmargin="0" leftmargin="0">
<form action="/sakai_quiz_tool_handler/" method="post" name="frm" id="form1">
<table width="100%" border="0">
  <tr>
    <td colspan="4" align="left" bgcolor="#CABFC1">
      <p class="style1"><h2>Sakai Quiz Generator</h2></p>
      <p class="style16">Use this program to generate a QTI XML file that's required to import questions from a WebCT quiz or a Word Doc to a Sakai quiz.<br>&nbsp; </p>    </td>
  </tr>
  <tr>
    <td width="13%" bgcolor="#EDEDED">
      <label class="style15"><span class="style15">Quiz Name:</span></label>
    </td>
    <td width="35%" align="left" valign="middle" bgcolor="#EDEDED" class="style16">
      <input name="quiz_name" type="text" class="style15" size="50" />
    </td>
    <td width="52%" colspan="2" align="left" valign="middle" bgcolor="#EDEDED">
      <label></label>
    <span class="style16">Please DON'T use &quot;#, %,&amp;, *, ?,&lt;,&gt;, /, \&quot; in the Quiz Name </span></td>
  </tr>
  <tr>
      <td align="left" valign="top" bgcolor="#EDEDED" class="style15">Quiz Instructions: 
      </td>
    <td align="left" valign="top" bgcolor="#EDEDED">
      <textarea name="quiz_description" cols="47" rows="2" class="style15"></textarea>
    </td>
    <td colspan="2" align="left" valign="top" bgcolor="#EDEDED">
      <span class="style16">Optional</span> 
    </td>
  </tr>
  <tr>
    <td rowspan="2" align="left" valign="top" bgcolor="#EDEDED"><span class="style15">Quiz Questions: </span></td>
    <td rowspan="2" align="left" valign="top" bgcolor="#EDEDED">
      <textarea name="quiz_data" cols="47" rows="20" class="style15"></textarea>
      <br><br><span class="style7">
      <input type="button" value="Submit" onClick="doSubmit();"> 
    </span>    <span class="style7">
    <input type="reset" value="Reset">
    </span></td>
    <td colspan="2" align="left" valign="top" bgcolor="#EDEDED">
      <p class="style16">Please copy &amp; paste the questions 
        from a WebCT quiz or Word Doc here in the format as below:</p>
     </td>
  </tr>
  <tr>
    <td align="left" size="50%" valign="top" bgcolor="#EDEDED"><p class="style16"><strong>For multiple choice questions:</strong></p>
      <p class="style16"><span class="style18">
        Question Number</span><span class="style25"> (Number of points)</span> <span class="style26"><br>
        Question body</span></p>
      <p class="style16"><span class="style23">*a. Choice A (* indicates the correct answer) </span><br />
        b. Choice B <br />
        c. Choice C <br />
        d. Choice D <br />
  <span class="style22">Save answer (Save answer indicates the end of a question) </span></p>
      <p class="style16"><strong>Example: </strong><br />
        Question 1  (10 points)<br> 
        When did America declare independence from Great Britain?</p>
      <p class="style16"> 
       *a. 07/04/1776 <br />
        b. 04/07/1776 <br />
        c. 07/04/1767 <br />
        d. 04/07/1767</p>
      <p class="style16">Save answer</p>
      <p class="style16">Question 2  (10 points)<br>The U.S.'s greatest trading partner is Canada.</p>
      <p class="style16">*a.True <br />
        b. False </p>
      <span class="style16">
      <label></label>
      </span>
      <p class="style16">Save answer</p>    </td>
    <td align="left" size="50%" valign="top" bgcolor="#EDEDED"><p class="style17">For fill in Blank Questions: </p>
      <p class="style16"><span class="style18">Question Number</span> <span class="style25">(Number of points)</span><br>
        Question body</p>
      <p class="style27">* Correct answer</p>
      <p class="style28">Save answer   (Save answer indicates the end of a question) </p>
      <span class="style17">Example: </span>
      <p class="style16">Question 3  (10 points)<BR>What color is a violet?  ____</p>
      <p class="style16">*Blue</p>
    <p class="style16">Save Answer </p></td>
  </tr>
  <tr>
    <td colspan="4" align="left" valign="top">
    </td>
  </tr>
</table>
</form>
</body>

<script language="JavaScript">
function cleanUp () {
	var quiz_data = document.frm.quiz_data.value;
	quiz_data = quiz_data.replace(/\\\.\\s\\t\\n\\n/g,". ");
	document.frm.quiz_data.value = quiz_data;
}

function doSubmit() {
	cleanUp();
	if (document.frm.quiz_name.value == "") {
		alert("quiz name should not be emplty");
		document.frm.quiz_name.focus();
	} else if (document.frm.quiz_data.value == "") {
		alert("quiz questions should not be emplty");
		document.frm.quiz_data.focus();
	} else {
		cleanUp();
	   document.frm.submit();
   }
}	    
        </script>
</html>

EOF
;
