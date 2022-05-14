var today = new Date();
var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18')
var sheet = ss.getSheetByName("Form Responses 1")
var emailLog = ss.getSheetByName("Email log")
var lineSheet = ss.getSheetByName("LINE")
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

function get_si(type, value){
  var typeList = sheet.getRange(1, headers().indexOf(type), sheet.getLastRow(), 1).getValues().flat()
  if (typeList.indexOf(value) != -1){return typeList.indexOf(value)+1}
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
  
  sendGformLink(null, lineId=lineId, resp=resp)
  
  //Simultanious line registrations bug fix (one registration will overwrite other one if no time gap)
  for (var i = 1; i < 200; i++){
    Utilities.sleep(2000)
    Logger.log("registrations bugfix"+lineId+" attempt "+i)
    lineAndName = lineSheet.getRange(426, 2, lineSheet.getLastRow(), 2).getValues()
    lineAndName.reverse()
    // Logger.log(lineAndName)
    for (const x of lineAndName) {if (x[0] == lineId) {
      Logger.log("registrations bugfix"+lineId+" attempt "+i+"OK"); return}}
    var r= lineSheet.getRange(lineSheet.getLastRow()+1, 2, 1, 3)
    Logger.log("registrations bugfix"+lineId+" attempt "+i+" write on "+lineSheet.getLastRow()+1)
    r.setValues([[lineId, displayName]])
    }


  
  // for (var i = 1; i < 200; i++){
  //   Utilities.sleep(2000)
  //   Logger.log("registrations bugfix"+lineId+" attempt "+i)
  //   respIds = sh.getRange(1, 1, sh.getLastRow(), 1).getValues()
  //   for (var i = 1; i < respIds.length; i++) { 
  //     if (resp.getId() == respIds[i]) {Logger.log("registrations bugfix"+lineId+" attempt "+i+"OK");return}}
  //   var r= sh.getRange(sh.getLastRow()+1, 1, 1, 3)
  //   Logger.log("registrations bugfix"+lineId+" attempt "+i+" write on "+sh.getLastRow()+1)
  //   r.setValues([[resp.getId(), lineId, displayName]])
  //   }

}

function respFromLine(lineId){ //=> resp
  var respSh = ss.getSheetByName("student_line")
  lineIds = respSh.getRange(1, 2, respSh.getLastRow(), 1).getValues()
    for (var i = 1; i < lineIds.length; i++) { 
      if (lineId == lineIds[i]) {respId = respSh.getRange(i+1, 1, 1, 1).getValue(); break}}
  return form.getResponse(respId)//.getEditResponseUrl()
}

function form_submit(e){ //triggered from registration form
  Logger.log(JSON.stringify(e))
  var lineId
  var firstName = sheet.getRange(e.range['rowStart'],headers().indexOf("firstName")).getValue()
  var studentId = sheet.getRange(e.range['rowStart'],headers().indexOf("studentId")).getValue()
  var state = sheet.getRange(e.range['rowStart'],headers().indexOf("state")).getValue()
  
  if (studentId == defaultStudentId){ //automatic for response, link Line id to default form registration
    sheet.getRange(e.range['rowStart'],headers().indexOf("state")).setValue("reg0")
    sheet.getRange(e.range['rowStart'],headers().indexOf("lastUpdateDate")).setValue(today)
    //get lineId from LINE sheet
    loop1:
      for (var i = 1; i < 200; i++){
        Logger.log("registrations bugfix"+firstName+" reading attempt "+i)
        lineAndName = lineSheet.getRange(426, 2, lineSheet.getLastRow(), 2).getValues()
        lineAndName.reverse()
        // Logger.log(lineAndName)
        for (const x of lineAndName) { //get lineID
          if (x[1] == firstName) {Logger.log("found "+x);  lineId = x[0]; break loop1}
        }
        Utilities.sleep(2000)
      // Logger.log(lineAndName)
      
          //wait and try again if no lineID   
        }
    Logger.log(lineId+" registration first form submit")
    sheet.getRange(e.range['rowStart'],headers().indexOf("lineId")).setValue(lineId)
    return
    }

  else if(state.slice(0,3) == 'reg'){ //1st manual form response
    sh = ss.getSheetByName("student_line")
    respIds = sh.getRange(1, 1, sh.getLastRow(), 1).getValues()
    item=form.getItemById(1438401958) //studentID
    // item=form.getItemById(1080414757) // firstName
    var respId   
    var classNumber = sheet.getRange(e.range['rowStart'],headers().indexOf("classNumber")).getValue()
    var classType = sheet.getRange(e.range['rowStart'],headers().indexOf("classType")).getValue()
    var textbook = sheet.getRange(e.range['rowStart'],headers().indexOf("texbook")).getValue()
    var startChapter = sheet.getRange(e.range['rowStart'],headers().indexOf("startChapter")).getValue()
    for (var i = 1; i < 200; i++){ //simultaneous registrations bugfix
      var lineId = sheet.getRange(e.range['rowStart'],headers().indexOf("lineId")).getValue()
      if (lineId){break}
      Logger.log("1st manual form submission no line attemt: "+i)
      Utilities.sleep(2000)
    }
    sendAnkiInstructions(e.range['rowStart'])  
    sheet.getRange(e.range['rowStart'],headers().indexOf("state")).setValue("new")
    Logger.log('status update to new ok')
    sheet.getRange(e.range['rowStart'],headers().indexOf("lastUpdateDate")).setValue(today)
    //input class data
    update_class(studentId, classNumber, classType, textbook, startChapter)
        
  }
  
  else{//other manual form response
    var lineId = sheet.getRange(e.range['rowStart'],headers().indexOf("lineId")).getValue()
    if(!lineId){
      sheet.getRange(e.range['rowStart'],headers().indexOf("agreement")).setValue(studentId)
      sheet.getRange(e.range['rowStart'],headers().indexOf("studentId")).setValue("fromBlankForm")
      sheet.getRange(e.range['rowStart'],headers().indexOf("state")).setValue("tblank")
      sendWrongForm(e.range['rowStart'])
    }
    GmailApp.sendEmail('self-learning@mtc.ntnu.edu.tw', 'INFO UPDATE: '+firstName, JSON.stringify(e))
  }
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
        if (action["emailTemplate"]=="regReminder"){
          sendRegReminder(studentIndex)
        }
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
        else if (action["emailTemplate"].slice(0,-1)=="bookAdded"){
          sendBookAdded(studentIndex, action["emailTemplate"].slice(-1))
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

function run_afc(sId, bookNr = null){
  url="http://35.206.234.133/autoflashcards/run/"
  Logger.log(url)
  if (bookNr == null) {url=url+"sid/"+sId}
  else {url+="book/"+sId+"/"+bookNr}
  Logger.log("autorun, url:"+url)
  try{resp = UrlFetchApp.fetch(url); Logger.log(resp)}
  catch(err){Logger.log('autoconnect error; name: '+err.name+'/message: '+err.message)}
  
}

function line_response(e){ //triggered from 'line response' form
  Logger.log(JSON.stringify(e))
  input = e.values[1]
  if (input.length <= 10) {si = get_si('studentId', parseFloat(input)); Logger.log(si)} 
  else {si = get_si('lineId', input); Logger.log(si)}

  if (si){
  if (e.values[2]=='answer LINE'){
    pushMsg(getData(si)['lineId'], e['values'][3])
    append_email_log(si, 'custom reply', 'line')
  }
  else if (e.values[2]=='run'){run_afc(sId)}
  else if (e.values[2].slice(0,3) == 'Add'){run_afc(sId, bookNr=e.values[2].slice(-1))}
  else if (e.values[2]=='ask class update'){sendTermUpdateReminder(si)}
  }
  else {
    pushMsg(input, e['values'][3])
  }
}
