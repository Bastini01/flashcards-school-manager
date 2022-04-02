var today = new Date();
var ss = SpreadsheetApp.getActiveSpreadsheet();
var sheet = ss.getSheetByName("Form Responses 1");
var emailLog = ss.getSheetByName("Email log");
var range = sheet.getRange(1, sheet.getLastRow(), 1, sheet.getLastColumn());

function headers(){ return getHeaders(sheet, range, 1); } 

function handleRegistration(){ 
  // finds the first row without status (necessary to avoid 'trigger to slow bug')
  for (var i =1; i < sheet.getLastRow()+3; ++i){
    if(sheet.getRange(i, headers().indexOf("state")+2).getValue()==''){
      var si=i
      break;
    }
  }
  sheet.getRange(si,headers().indexOf("state")+1).setValue("new");
  sheet.getRange(si,headers().indexOf("lastUpdateDate")+1).setValue(today);
  sendOnboarding(si)
}

function handleDesktopRequest(rq){

  var obj = JSON.parse(rq);
  var actions = Object.keys(obj).map(key => ( obj[key] ));

  for (var i = 0; i < actions.length; ++i) {

    var action=actions[i];
    Logger.log(action);
    var studentIndex=action["studentIndex"];
    if (action["statusUpdate"]) {
      sheet.getRange(studentIndex, 12).setValue(action["statusUpdate"]);
      sheet.getRange(studentIndex, headers().indexOf("lastUpdateDate")+1).setValue(today);
    }
    if (action["chapterUpdate"]) {
      sendChapterUpdate(studentIndex, action["chapterUpdate"]);
    }
    if (action["emailTemplate"]){
      if (action["emailTemplate"]=="wrongPassword"){
        sendWrongPassword(studentIndex)
      }
      else if (action["emailTemplate"]=="activatedMail"){
        sendActivated(studentIndex)
      }
      else if (action["emailTemplate"]=="reminder0"){
        sendReminder0(studentIndex)
      }
      else if (action["emailTemplate"][0].slice(0,6)=="weekly"){
        sendWReport(studentIndex, action["emailTemplate"])
      }
    }
  }


  return actions
}
