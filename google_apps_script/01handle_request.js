var today = new Date();
// var ss = SpreadsheetApp.getActiveSpreadsheet()
var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18')
var sheet = ss.getSheetByName("Form Responses 1")
var emailLog = ss.getSheetByName("Email log")
var range = sheet.getRange(1, sheet.getLastRow(), 1, sheet.getLastColumn())
var form = FormApp.openById('1LUX5E3MmT8EbHD1wv0D8tOe3hBEuP0cKUapJKB4eWWw')

defaultStudentId = '?'

function headers(){
  return ['','timestamp', 'email', 'firstName', 'lastName', 'studentId', 'classNumber', 'classType', 'texbook', 'phoneOperatingSystem', 'startChapter','agreement', 'state', 'lastUpdateDate', 'lineId'] } 

function getData(studentIndex){
  var email = sheet.getRange(studentIndex,headers().indexOf('email')).getValue() 
  var sId = sheet.getRange(studentIndex,headers().indexOf('studentId')).getValue()
  var firstName = sheet.getRange(studentIndex,headers().indexOf('firstName')).getValue()
  var pw = email.substring(0, email.indexOf("@"))
  var lineId = sheet.getRange(studentIndex,headers().indexOf('lineId')).getValue()
  var state = sheet.getRange(studentIndex,headers().indexOf('state')).getValue()
  return {email, sId, firstName, pw, lineId, state}
}

function data_from_line(lineId){
  
}

function registration_from_line(lineId, displayName){

  classTypeChoice = form.getItemById(1337875648).asMultipleChoiceItem().getChoices()[0].getValue()
  phoneOS = form.getItemById(840060439).asMultipleChoiceItem().getChoices()[0].getValue()
  textBook = form.getItemById(390088629).asListItem().getChoices()[0].getValue()
  startChap = form.getItemById(328724812).asListItem().getChoices()[0].getValue()
  agreement = [form.getItemById(639898031).asCheckboxItem().getChoices()[0].getValue()]

  itemResponses=[
    form.getItemById(196710778).asTextItem().createResponse(""),
    form.getItemById(1080414757).asTextItem().createResponse(displayName),
    form.getItemById(276034900).asTextItem().createResponse(""),
    form.getItemById(1438401958).asTextItem().createResponse(defaultStudentId),
    form.getItemById(642329067).asTextItem().createResponse(""),
    form.getItemById(1337875648).asMultipleChoiceItem().createResponse(classTypeChoice),
    form.getItemById(390088629).asListItem().createResponse(textBook),
    form.getItemById(328724812).asListItem().createResponse(startChap),
    form.getItemById(840060439).asMultipleChoiceItem().createResponse(phoneOS),
    form.getItemById(639898031).asCheckboxItem().createResponse(agreement)
  ]
  resp = form.createResponse()
  itemResponses.forEach(
    w => resp.withItemResponse(w)
  )
  resp = resp.submit()

  var sh = ss.getSheetByName("student_line")
  var r= sh.getRange(sh.getLastRow()+1, 1, 1, 2)
  r.setValues([[resp.getId(), lineId]])
  Logger.log(lineId+" noted down")

  var msgText="Hi!\n"+
          "Welcome to MTC self-learning\n"+
          "In order to set up your account, please fill in the form below:\n"+
          resp.getEditResponseUrl()

  pushMsg(lineId, msgText)

  //Simultanious line registrations bug fix (one registration will overwrite other one if no time gap)
  for (var i = 1; i < 200; i++){
    Utilities.sleep(1000)
    respIds = sh.getRange(1, 1, sh.getLastRow(), 1).getValues()
    for (var i = 1; i < respIds.length; i++) { 
      if (resp.getId() == respIds[i]) {return}}
    var r= sh.getRange(sh.getLastRow()+1, 1, 1, 2)
    r.setValues([[resp.getId(), lineId]])
    }
}

function testlinereg(){registration_from_line("U02e268a357d377f429911a1fd87c52e4", "abdc")}

function form_submit(e){
  Logger.log(JSON.stringify(e));
  if (e.values[4] == defaultStudentId){
    sheet.getRange(e.range['rowStart'],headers().indexOf("state")).setValue("treg"); return
    }
  sh = ss.getSheetByName("student_line")
  respIds = sh.getRange(1, 1, sh.getLastRow(), 1).getValues()
  item=form.getItemById(1438401958)
  var respId, lineId
  var studentId = sheet.getRange(e.range['rowStart'],headers().indexOf("studentId")).getValue()
  var classNumber = sheet.getRange(e.range['rowStart'],headers().indexOf("classNumber")).getValue()
  var classType = sheet.getRange(e.range['rowStart'],headers().indexOf("classType")).getValue()
  var textbook = sheet.getRange(e.range['rowStart'],headers().indexOf("texbook")).getValue()
  var startChapter = sheet.getRange(e.range['rowStart'],headers().indexOf("startChapter")).getValue()

  for (const x of form.getResponses()) { 
    // Logger.log(x.getResponseForItem(item).getResponse())
    if (x.getResponseForItem(item).getResponse() == studentId) {
          respId = x.getId()
          break
      }   
    }
  Logger.log(respId)
  // row = respIds.indexOf(respId)+1
  for (var i = 1; i < respIds.length; i++) { 
    if (respId == respIds[i]) {
          lineId = sh.getRange(i+1, 2).getValue()
          break
      }
   
   }
  if (!lineId){
    sheet.getRange(e.range['rowStart'],headers().indexOf("agreement")).setValue(studentId);
    sheet.getRange(e.range['rowStart'],headers().indexOf("studentId")).setValue("fromBlankForm");
    sendWrongForm(e.range['rowStart'])
    return
    }
  Logger.log(lineId)
  sheet.getRange(e.range['rowStart'],headers().indexOf("lineId")).setValue(lineId)
  sheet.getRange(e.range['rowStart'],headers().indexOf("state")).setValue("new")
  Logger.log('status update to new ok')
  sheet.getRange(e.range['rowStart'],headers().indexOf("lastUpdateDate")).setValue(today)
  //input class data
  update_class(studentId, classNumber, classType, textbook, startChapter)
  
  sendAnkiInstructions(e.range['rowStart'])  

}

function handle_update_submission(e){ //trigger comes from update form
  Logger.log(JSON.stringify(e))
  studentId = e['values'][2]
  if (e['values'][4]){
    classNumber = parseFloat(e['values'][4])
    classType = e['values'][5]
    textbook = e['values'][6]
    startChapter = e['values'][7]
  update_class(studentId, classNumber, classType, textbook, startChapter)
  }
  else{
    sId = parseFloat(studentId)
    update_status(sId, 'tOut')}
}

function update_class(studentId, classNumber, classType, textbook, startChapter){
  var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18')
  var bookNr = textbook.match(/\d+/)[0]
  var chapNr = startChapter.match(/\d+/)[0]
  if (classType[0] == 'R'){type = 2} else {type = 1}
  sc = ss.getSheetByName("student_class")
  var r= sc.getRange(sc.getLastRow()+1, 1, 1, 2);
  r.setValues([[classNumber, studentId]])
  classSheet = ss.getSheetByName("class")
  classIds = classSheet.getRange(1, 1, classSheet.getLastRow(), 1).getValues().flat()
  if (!classIds.includes(classNumber)) {
        r = classSheet.getRange(classSheet.getLastRow()+1, 1, 1, 5)
        r.setValues([[classNumber,"999",'22spring',type,bookNr+','+chapNr]])
        Logger.log('class: '+classNumber+' created')
    }
}

function update_status(studentId, status){
  var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18')
  var sheet = ss.getSheetByName("Form Responses 1")
  var studentIds = sheet.getRange(1,headers().indexOf("studentId"), sheet.getLastRow(),1).getValues().flat()
  row = studentIds.indexOf(studentId)+1
  sheet.getRange(row, headers().indexOf('state')).setValue(status)
}

function test_request(){
  // action = {studentIndex=113.0, emailTemplate=[weekly220321, {time=1 minute, otbWords=0.0, completion=[null, null], chaps-words=[], learning=0.0, top=[], reviews=0.0, pending=24.0, tbWords=0.0, chaps=0.0, hours=0.0, lastRev=1.647216E12, pendingLearning=[[[2.0, 4.0], 24.0, 0.0, 6 minutes]]}]}
  // var actions = Array((studentIndex=2.0, emailTemplate="suppHours23"))
  // var actions = JSON.stringify(actions)
  // Logger.log(actions)

  rq = '{"0":{"studentIndex":2,"emailTemplate":"suppHours24"}}'
  handleDesktopRequest(rq)
  // var obj = JSON.parse(rq)
  // Logger.log(obj)
  // var actions = Object.keys(obj).map(key => ( obj[key] ))
  // Logger.log(actions)
  // for (var i = 0; i < actions.length; ++i) {
  //   var time1 = new Date()
  //   var action=actions[i]
  //   Logger.log(action)
  // }
}

function handleDesktopRequest(rq){

  var obj = JSON.parse(rq)
  var actions = Object.keys(obj).map(key => ( obj[key] ))
  
  for (var i = 0; i < actions.length; ++i) {
    var time1 = new Date()
    var action=actions[i]
    Logger.log(action)
    // student actions
    if (action["studentIndex"]) {
        var studentIndex=action["studentIndex"]
      if (action["statusUpdate"]) {
        sheet.getRange(studentIndex, 12).setValue(action["statusUpdate"]);
        sheet.getRange(studentIndex, headers().indexOf("lastUpdateDate")).setValue(today);
      }
      if (action["chapterUpdate"]) {
        sendChapterUpdate(studentIndex, action["chapterUpdate"]);
      }
      if (action["emailTemplate"]){
        if (action["emailTemplate"]=="termUpdate"){
          sendTermUpdate(studentIndex)
        }
        if (action["emailTemplate"]=="wrongPassword"){
          sendWrongPassword(studentIndex)
        }
        if (action["emailTemplate"]=="notActivated"){
          sendNotActivated(studentIndex)
        }
        else if (action["emailTemplate"]=="activatedMail"){
          sendActivated(studentIndex)
        }
        else if (action["emailTemplate"]=="reminder0"){
          sendReminder0(studentIndex)
        }
        else if (action["emailTemplate"][0].slice(0,3)=="acc"){
          sendAccReport(2, action["emailTemplate"])
        }
        else if (action["emailTemplate"][0].slice(0,6)=="weekly"){
          sendWReport(studentIndex, action["emailTemplate"])
        }
        else if (action["emailTemplate"][0].slice(0,5)=="daily"){
          sendDReport(studentIndex, action["emailTemplate"])
        }
        else if (action["emailTemplate"].slice(0,9)=="suppHours"){
          h=action["emailTemplate"].slice(9,10)
          sh=action["emailTemplate"].slice(10,11)
          add_supp_hours(getData(studentIndex).sId, h)
          sendSuppHours(studentIndex, h, sh)
        }        
        else if (action["emailTemplate"]=="custom"){
          sendCustom(studentIndex)
        }
      }
    }
    // class actions
    else if (action["emailTemplate"][0]=="classWeekly"){
          sendClassWeekly(action["emailTemplate"][1])
        }
    // send log
    else if (action["emailTemplate"][0]=="log"){
          GmailApp.sendEmail('pierrehenry.bastin@gmail.com',"Auoflashcards log",action["emailTemplate"][1])
        }
    else if (action["emailTemplate"][0]=="statsReport"){
      GmailApp.sendEmail('pierrehenry.bastin@gmail.com',"Auoflashcards stats","display error", {htmlBody: action["emailTemplate"][1]})
    }

    var time2 = new Date()
    var dif = Math.abs(time2-time1)
    if (dif<1000){Utilities.sleep(1000-dif)}
    }

  
  return actions
  
}

function auto_connect(lineId){
  lineIds = sheet.getRange(1, headers().indexOf('lineId'), sheet.getLastRow(), 1).getValues().flat()
  if (lineIds.indexOf(lineId) != -1){
    si = lineIds.indexOf(lineId)+1
    sId = getData(si)['sId'].toString(); Logger.log(sId)
    if (getData(si)['state']=='new'){
      sheet.getRange(si, headers().indexOf('state')).setValue('newwaiting')
      try{resp = UrlFetchApp.fetch("http://35.206.234.133/autoflashcards/run/sid/"+sId); Logger.log(resp)}
      catch(err){Logger.log('autoconnect error; name: '+err.name+'/message: '+err.message)}
    }

  }
}
