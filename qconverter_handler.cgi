#!/usr/bin/perl
#!c:/perl/bin/Perl.exe

## ##################################################################################################
##  Filename:   qconverter_handler.pl
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

use CGI;
use strict;
no strict 'subs';

print "Content-Type: text/html\n\n";

#get form variables
my $q = new CGI;
my $quiz_name   = $q->param('quiz_name'); 
my $quiz_data  = $q->param('quiz_data');
my $quiz_description  = $q->param('quiz_description');

#make sure required fields are not empty
if ($quiz_name eq "" or $quiz_data eq "") {
    print "quiz name or quiz data should not be empty.";
    exit;
}

#repalace Spanish charaters in data
$quiz_name = &replaceSpanishChars($quiz_name);
$quiz_data = &replaceSpanishChars($quiz_data);
$quiz_description = &replaceSpanishChars($quiz_description);

 
our $sakai_xml = "";  #hold the content of xml, global variable

#creat a filename for the xml
my $sakai_xml_filename = $quiz_name;
$sakai_xml_filename =~ s/\s/\_/g;
$sakai_xml_filename .= ".xml";

### NOTE: Modify these following variables to meet your needs ###
my $xml_path = "/www/webapps/output/"; #path where the xml file is saved on the server
my $xml_link = "/output/$sakai_xml_filename"; #the link to download the xml file 


our %spanishCharsHash = ( 
         "Á" , "&#193;",
         "á" , "&#225;",
         "É" , "&#201;",
         "é" , "&#233;",
         "Í" , "&#205;",         
         "í" , "&#237;",
         "Ñ" , "&#209;",
         "ñ" , "&#241;",
         "Ó" , "&#211;",
         "ó" , "&#243;",
         "Ú" , "&#218;",
         "ú" , "&#250;",
         "Ü" , "&#220;",
         "ü" , "&#252;",
         "«" , "&#171;",
         "»" , "&#187;",
         "¿" , "&#191;",
         "¡" , "&#161;"
    );
 
my $output = "";             
$output .= <<EOF;
<head>
<title>Sakai Quiz Converter</title>
<style type="text/css">
body {  text-decoration: none;
        font-family: "Verdana, Arial, Helvetica, sans-serif";
        font-size: 9px;
        background-color:#EDEDED; 
}
</style>
</head>
<body topmargin="0" leftmargin="0">
<table width="100%" border="0">
  <tr>
    <td>
      Download the XML file and use the Sakai's Tests and Quizzes Import feature to import the quiz. <br>
      <ul>
       <li><B>PC User:</B> Please right click <a href='$xml_link'>$sakai_xml_filename</a> to download the file.<br></li>
       <li><B>Mac User:</B> Please CTRL click <a href='$xml_link'>$sakai_xml_filename</a> to download the file.<br><br></li>
      </ul>
    </td>
  </tr>  


EOF
;


#get the xml contents and store in $sakai_xml. There are three parts: top, middle, and bottom
&getTopXML($quiz_name);


my @data = split(/\n/, $quiz_data);
my ($question_number,$question_points,$question,$question_type,$correct_answer);
my @answer; # store answers for multiple choice question
my $ind = 0;

#loop through the @data and process the data 
for (my $i=0; $i<=$#data; $i++) {
    chop($data[$i]) if $data[$i] =~ /\r$/;
    $data[$i] =~ s/^\s+//g; # remove the leading space
   if ($data[$i] ne "" and $data[$i] ne "Answer: ") {
        
       if ($data[$i] =~ /^Question(\s+)(\d+)(\s+)\((\d*\.?\d*)(\s+)point(s?)/) {
           $question_number = $2;
           $question_points = $4;
        }elsif ($data[$i] =~ /^\*/) {
            if ($data[$i] =~ /^\*([a-zA-Z])\.(\s*)(.*)/) {
                $correct_answer = $1;
                $answer[$ind] = $3;
                $ind++;
                $question_type = "Multiple Choice";
            }
                        elsif ($data[$i] =~ /^\*\s/) {
                $correct_answer = "";
            }
            elsif ($data[$i] =~ /^\*(.*)/) {
                $correct_answer = $1;
                $question_type = "Fill in Blank";
            } 
        }elsif ($data[$i] =~ /^([a-zA-Z])\.(\s*)(.*)/) {
            $answer[$ind] = $3;
            $ind++;
        }elsif ($data[$i] =~ /^Save answer/) {
            $output .= "<tr><td>\n";
            $output .= "Question $question_number: $question<br>";
            $output .= "Point: $question_points<br>";
            $output .= "Correct Answer: $correct_answer<br>";
            $output .= "Question Type: $question_type<br>";
            if ($question_type eq "Multiple Choice") {
                for (my $j=0; $j<=$#answer; $j++) {
                    my $answer_number = $j+1;
                  $output .=  "&nbsp; answer $answer_number: $answer[$j] <br>";
              }
           }
           
           
           #check for missing data
           if ($question eq "") {
               print "Error!!! no question for Question $question_number <input type=button onClick=history.go(-1) value='Go Back'>";
               exit;
            }elsif ($question_points eq "") {
                print "Error!!! no points for Question $question_number <input type=button onClick=history.go(-1) value='Go Back'>";
                exit;
            }elsif ($correct_answer eq "") {
                print "Error!!! no correct answer for Question $question_number <input type=button onClick=history.go(-1) value='Go Back'>";
                exit;
            }elsif ($question_type eq "") {
               print "Error!!! no question type for Question $question_number <input type=button onClick=history.go(-1) value='Go Back'>";
               exit;
           }
           else {
               $question =~ s/(\x93|\x94)/"/g;
               &getMiddleXML($question,$correct_answer,$question_type,@answer);
           }
            $output .= "<br></td></tr>";
            
            #reset values
            $question_number = "";
           $question_points = "";
            $question_type = "";
            $question = ""; 
            @answer  = ();
            $ind = 0; 
        } else {
            $question .= "$data[$i] ";
        }  
    }
}

$output .= "</table>";
$output .= "</body>";
print $output;

&getBottomXML();

#write the xml to a file
open (FILE,">$xml_path$sakai_xml_filename");
print FILE $sakai_xml;
close FILE;



sub replaceSpanishChars {
    my $str = shift;
    while (my ($key, $value) = each(%spanishCharsHash)){
      $str =~ s/$key/$value/g;
  }
  
  return $str;
}
     

sub getMiddleXML {
    my ($question,$correct_answer,$question_type,@answer) = @_;
    if ($question_type eq "Multiple Choice") {      
        $sakai_xml .=  <<EOF;
  <item ident="" title="Multiple Choice">
  <duration></duration>
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>qmd_itemtype</fieldlabel>
        <fieldentry>Multiple Choice</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>TEXT_FORMAT</fieldlabel>
        <fieldentry>HTML</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>ITEM_OBJECTIVE</fieldlabel>
        <fieldentry></fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>ITEM_KEYWORD</fieldlabel>
        <fieldentry></fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>ITEM_RUBRIC</fieldlabel>
        <fieldentry></fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>hasRationale</fieldlabel>
        <fieldentry>false</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
<rubric view="All">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>
      </material>
    </rubric>
  <presentation label="">
    <flow class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"><![CDATA[$question]]></mattext>
      </material>
      <material>
        <matimage embedded="base64" imagtype="text/html" uri=""></matimage>
      </material>
      <response_lid ident="MCSC" rcardinality="Single" rtiming="No">
        <render_choice shuffle="No">
EOF
;
   #fill in the answers
    for (my $j=0; $j<=$#answer; $j++) {
        my $char = chr(($j+65));
        $sakai_xml .=  <<EOF;
          <response_label ident="$char" rarea="Ellipse" rrange="Exact" rshuffle="Yes">
            <material>
              <mattext charset="ascii-us" texttype="text/plain" xml:space="default"><![CDATA[$answer[$j]]]></mattext>
            </material>
            <material>
              <matimage embedded="base64" imagtype="text/html" uri=""></matimage>
            </material>
          </response_label>
EOF
;      
   }
   
    for (my $j=0; $j<=$#answer; $j++) {
        $sakai_xml .=  <<EOF;
   
   <response_label rarea="Ellipse" rrange="Exact" rshuffle="Yes"><material><mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>
</material>
</response_label>
<response_label rarea="Ellipse" rrange="Exact" rshuffle="Yes"><material><mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>
</material>
</response_label>

EOF
;
        }
    $sakai_xml .=  <<EOF;
   </render_choice>
      </response_lid>
    </flow>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar defaultval="0" maxvalue="$question_points" minvalue="0" varname="SCORE" vartype="Integer"></decvar>
    </outcomes>
      
EOF
;  
      ### response session
        for (my $j=0; $j<=25; $j++) {
            my $char = chr(($j+65));
            my $response = (lc($char) eq $correct_answer)? "Correct" : "InCorrect"; 
          $sakai_xml .=  <<EOF;
        <respcondition continue="No">
      <conditionvar>
        <varequal case="Yes" respident="MCSC">$char</varequal>
      </conditionvar>
      <setvar action="Add" varname="SCORE">0.0</setvar>
      <displayfeedback feedbacktype="Response" linkrefid="$response"></displayfeedback>
      <displayfeedback feedbacktype="Response" linkrefid="AnswerFeedback"><![CDATA[null]]></displayfeedback>
    </respcondition>      
                 
EOF
;      
   }
      ### feedback session  
        for (my $j=0; $j<=$#answer; $j++) {
            my $char = chr(($j+65));
            my $order = "$char"."1";
          $sakai_xml .=  <<EOF;
   <itemfeedback ident="$order" view="All">
    <flow_mat class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>
      </material>
      <material>
        <matimage embedded="base64" imagtype="text/html" uri=""></matimage>
      </material>
    </flow_mat>
  </itemfeedback>
EOF
;
        }
        
        $sakai_xml .= <<EOF;
       </resprocessing> 
        <itemfeedback ident="Correct" view="All">
    <flow_mat class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


      </material>


      <material>
        <matimage embedded="base64" imagtype="text/html" uri=""></matimage>


      </material>


    </flow_mat>


  </itemfeedback>


  <itemfeedback ident="InCorrect" view="All">
    <flow_mat class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


      </material>


      <material>
        <matimage embedded="base64" imagtype="text/html" uri=""></matimage>


      </material>


    </flow_mat>


  </itemfeedback>

</item>

EOF
;
        
    }elsif ($question_type eq "Fill in Blank") {
       $sakai_xml .=  <<EOF;
    <item ident="" title="Fill in Blank">
  <duration></duration>


  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>qmd_itemtype</fieldlabel>


        <fieldentry>Fill In the Blank</fieldentry>


      </qtimetadatafield>


      <qtimetadatafield>
        <fieldlabel>TEXT_FORMAT</fieldlabel>


        <fieldentry>HTML</fieldentry>


      </qtimetadatafield>


      <qtimetadatafield>
        <fieldlabel>MUTUALLY_EXCLUSIVE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      <qtimetadatafield>
        <fieldlabel>ITEM_OBJECTIVE</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      <qtimetadatafield>
        <fieldlabel>ITEM_KEYWORD</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      <qtimetadatafield>
        <fieldlabel>ITEM_RUBRIC</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


    </qtimetadata>


  </itemmetadata>


   <rubric view="All">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


      </material>


    </rubric>


  <presentation label="FIB">
    <flow class="Block">
    
    
    <flow class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default">$question</mattext>


      </material>


    <material><mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>

</material>

<response_str ident="" rcardinality="Ordered" rtiming="No"><render_fib charset="ascii-us" columns="5" encoding="UTF_8" fibtype="String" prompt="Box" rows="1"></render_fib>

</response_str>

<material><mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>

</material>

</flow>


    </flow>


  </presentation>


  <resprocessing>
    <outcomes>
      <decvar defaultval="0" maxvalue="$question_points" minvalue="0" varname="SCORE" vartype="Integer"></decvar>


    </outcomes>


  <respcondition continue="Yes"><conditionvar><or><varequal case="No" respident="">$correct_answer</varequal>

</or>

</conditionvar>

<setvar action="Add" varname="SCORE">0</setvar>

</respcondition>

</resprocessing>


  <itemfeedback ident="Correct" view="All">
    <flow_mat class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


      </material>


      <material>
        <matimage embedded="base64" imagtype="text/html" uri=""></matimage>


      </material>


    </flow_mat>


  </itemfeedback>


  <itemfeedback ident="InCorrect" view="All">
    <flow_mat class="Block">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


      </material>


      <material>
        <matimage embedded="base64" imagtype="text/html" uri=""></matimage>


      </material>


    </flow_mat>


  </itemfeedback>


</item>


EOF
;
  }
}

sub getBottomXML {
    $sakai_xml .=  <<EOF;
     </section>
  </assessment>
 </questestinterop>
EOF
;
}
 
sub getTopXML {
    my $quiz_name = shift;
    $sakai_xml .= <<EOF;
<?xml version="1.0" encoding="UTF-8"?> 
<questestinterop>
  <assessment ident="" title="$quiz_name">
    <qticomment></qticomment>
    <duration>P</duration>
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>AUTHORS</fieldlabel>
        <fieldentry></fieldentry>
      </qtimetadatafield>
     <qtimetadatafield>
        <fieldlabel>CREATOR</fieldlabel>
        <fieldentry></fieldentry>
      </qtimetadatafield>      
      <qtimetadatafield>
        <fieldlabel>SHOW_CREATOR</fieldlabel>
        <fieldentry>True</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>SCALENAME</fieldlabel>
        <fieldentry>STRONGLY_AGREE</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>EDIT_AUTHORS</fieldlabel>
        <fieldentry>True</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>EDIT_DESCRIPTION</fieldlabel>
        <fieldentry>True</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>DISPLAY_TEMPLATE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      
       <qtimetadatafield>
        <fieldlabel>START_DATE</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>END_DATE</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>RETRACT_DATE</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>

      <fieldlabel>CONSIDER_START_DATE</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>CONSIDER_END_DATE</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>CONSIDER_RETRACT_DATE</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_END_DATE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_RETRACT_DATE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

     
     <qtimetadatafield>
        <fieldlabel>ASSESSMENT_RELEASED_TO</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

     <qtimetadatafield>
        <fieldlabel>EDIT_PUBLISH_ANONYMOUS</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_AUTHENTICATED_USERS</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
       <qtimetadatafield>
        <fieldlabel>ALLOW_IP</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>CONSIDER_ALLOW_IP</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>CONSIDER_USERID</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>USERID</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>PASSWORD</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_ALLOW_IP</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_USERID</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
      <qtimetadatafield>
        <fieldlabel>CONSIDER_DURATION</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>



      <qtimetadatafield>
        <fieldlabel>AUTO_SUBMIT</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_DURATION</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_AUTO_SUBMIT</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      
     <qtimetadatafield>
        <fieldlabel>NAVIGATION</fieldlabel>


        <fieldentry>LINEAR</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>QUESTION_LAYOUT</fieldlabel>


        <fieldentry>I</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>QUESTION_NUMBERING</fieldlabel>


        <fieldentry>CONTINUOUS</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_NAVIGATION</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_QUESTION_LAYOUT</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_QUESTION_NUMBERING</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
     <qtimetadatafield>
        <fieldlabel>LATE_HANDLING</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>MAX_ATTEMPTS</fieldlabel>


        <fieldentry>1</fieldentry>


      </qtimetadatafield>


      
      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_LATE_HANDLING</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_MAX_ATTEMPTS</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

     <qtimetadatafield>
        <fieldlabel>AUTO_SAVE</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_AUTO_SAVE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
      <qtimetadatafield>
        <fieldlabel>EDIT_ASSESSFEEDBACK</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>SUBMISSION_MESSAGE</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FINISH_URL</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_FINISH_URL</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
      <qtimetadatafield>
        <fieldlabel>FEEDBACK_DELIVERY</fieldlabel>


        <fieldentry>IMMEDIATE</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_AUTHORING</fieldlabel>


        <fieldentry>QUESTION</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_DELIVERY_DATE</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_FEEDBACK_DELIVERY</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_FEEDBACK_COMPONENTS</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_CORRECT_RESPONSE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_STUDENT_SCORE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_ITEM_LEVEL</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_SELECTION_LEVEL</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_GRADER_COMMENT</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_STATS</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_QUESTION</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>FEEDBACK_SHOW_RESPONSE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
      <qtimetadatafield>
        <fieldlabel>ANONYMOUS_GRADING</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>GRADE_SCORE</fieldlabel>


        <fieldentry>HIGHEST_SCORE</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>GRADEBOOK_OPTIONS</fieldlabel>


        <fieldentry>SELECTED</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_GRADEBOOK_OPTIONS</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_ANONYMOUS_GRADING</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_GRADE_SCORE</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
      <qtimetadatafield>
        <fieldlabel>BGCOLOR</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>BGIMG</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      


      <qtimetadatafield>
        <fieldlabel>EDIT_BGCOLOR</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      


      <qtimetadatafield>
        <fieldlabel>EDIT_BGIMG</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
     
      <qtimetadatafield>
        <fieldlabel>EDIT_ASSESSMENT_METADATA</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      

      <qtimetadatafield>
        <fieldlabel>EDIT_COLLECT_SECTION_METADATA</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>EDIT_COLLECT_ITEM_METADATA</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>ASSESSMENT_KEYWORDS</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>ASSESSMENT_OBJECTIVES</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>ASSESSMENT_RUBRICS</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>COLLECT_SECTION_METADATA</fieldlabel>


        <fieldentry>False</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>COLLECT_ITEM_METADATA</fieldlabel>


        <fieldentry>false</fieldentry>


      </qtimetadatafield>


      
      
    
      <qtimetadatafield>
        <fieldlabel>LAST_MODIFIED_ON</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


       
      
    <qtimetadatafield>
        <fieldlabel>LAST_MODIFIED_BY</fieldlabel>


        <fieldentry></fieldentry>


      </qtimetadatafield>


     
      
      
      <qtimetadatafield>
        <fieldlabel>templateInfo_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>assessmentAuthor_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>assessmentCreator_isInstructorEditable</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>description_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>dueDate_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>retractDate_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>anonymousRelease_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>authenticatedRelease_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>ipAccessType_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>passwordRequired_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>timedAssessment_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>timedAssessmentAutoSubmit_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>itemAccessType_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>displayChunking_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>displayNumbering_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>submissionModel_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>lateHandling_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>autoSave_isInstructorEditable</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>submissionMessage_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>finalPageURL_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>feedbackType_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>feedbackComponents_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>testeeIdentity_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>toGradebook_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>recordedScore_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>bgColor_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>bgImage_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>metadataAssess_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>metadataParts_isInstructorEditable</fieldlabel>


        <fieldentry>True</fieldentry>


      </qtimetadatafield>


      
      
      <qtimetadatafield>
        <fieldlabel>metadataQuestions_isInstructorEditable</fieldlabel>


        <fieldentry>true</fieldentry>


      </qtimetadatafield>


      
      
    </qtimetadata>


    <assessmentcontrol feedbackswitch="Yes" hintswitch="Yes" solutionswitch="Yes" view="All"></assessmentcontrol>


    <rubric view="All">
      <material>
        <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


      </material>


    </rubric>


    <presentation_material>
      <flow_mat class="Block">
        <material>
          <mattext charset="ascii-us" texttype="text/plain" xml:space="default"><![CDATA[$quiz_description]]></mattext>


        </material>


      </flow_mat>


    </presentation_material>


    <assessfeedback ident="Feedback" title="Feedback" view="All">
      <flow_mat class="Block">
        <material>
          <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


        </material>


      </flow_mat>


    </assessfeedback>


  <section ident="" title="Multiple Choice Questions">
  <qtimetadata>
    
     
    <qtimetadatafield>
      <fieldlabel>SECTION_OBJECTIVE</fieldlabel>


      <fieldentry></fieldentry>


    </qtimetadatafield>


    <qtimetadatafield>
      <fieldlabel>SECTION_KEYWORD</fieldlabel>


      <fieldentry></fieldentry>


    </qtimetadatafield>


    <qtimetadatafield>
      <fieldlabel>SECTION_RUBRIC</fieldlabel>


      <fieldentry></fieldentry>


    </qtimetadatafield>


  </qtimetadata>


  <presentation_material>
    <flow_mat class="Block">
    <material>
      <mattext charset="ascii-us" texttype="text/plain" xml:space="default"></mattext>


    </material>


    <material>
      <matimage embedded="base64" imagtype="text/html" uri=""></matimage>


    </material>


    </flow_mat>


  </presentation_material>


  <selection_ordering sequence_type="Normal">
       <selection>
        <sourcebank_ref></sourcebank_ref>


        <selection_number></selection_number>


      </selection>


     <order order_type="Sequential"></order>


  </selection_ordering>
    

EOF
;
}    