function customSender () {
  target= [2]
  for (var i = 0; i < target.length; i++){
    Logger.log(target[i]+", "+ getData(target[i]).email+", "+ getData(target[i]).firstName)
    // sendWrongPasswordMail(target[i])
    // sendChapterUpdateMail(target[i], [1,9,2])
    // sendActivatedMail(target[i])
    // sendCustomMail(target[i])
    sendReminder0(target[i])
  }
  
}

function autoArray(){
  start=40
  end=49
  Logger.log([...Array(end - start + 1).keys()].map(x => x + start))
}

function fillTemplateA(template) {
  template.firstName=getData.firstName;
  template.emailAddress=getData.email;
  template.ankiwebPassword=getData.pw;
  return template.evaluate().getContent();
}

function getData(studentIndex){
  var dataRange = sheet.getRange(studentIndex, 1, 1, sheet.getLastColumn());
  objects = getRowsData(sheet, dataRange, 1);
  var email = sheet.getRange(studentIndex,2).getValue();  
  var rowData = objects[0];
  var sId = rowData.studentId
  var firstName = rowData.firstName
  var pw = email.substring(0, email.indexOf("@"))
  var lineId = rowData.lineId;
  return {email, sId, firstName, pw, lineId}
}

function append_email_log(studentIndex, templateName, type){
  if (type==null){type='gmail'}
  var dataRange = emailLog.getRange(emailLog.getLastRow()+1, 1, 1, 5);
  var values = [[today, getData(studentIndex).sId, getData(studentIndex).firstName, templateName, type]];
  dataRange.setValues(values);
}

function sendOnboarding(si){
  var tn = 'onboarding-template';
  var template = HtmlService.createTemplateFromFile(tn);
  var emailText = fillTemplateA(template);
  var subject = "MTC automated flashcards instructions - MTC自動化字卡說明";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}

function sendActivated(si) {
  var tn = 'activated_template';
  var template = HtmlService.createTemplateFromFile(tn);
  template.firstName=getData(si).firstName;
  var emailText = template.evaluate().getContent();
  var subject = "MTC automated flashcards activated - MTC自動化字卡建立成功";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}

function sendWrongPassword(si) {
  var tn = 'wrong_password_template';
  var template = HtmlService.createTemplateFromFile(tn);
  var emailText = fillTemplateA(template);
  var subject = "MTC automated flashcards password error - MTC自動化字卡錯誤";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}

function sendChapterUpdate(si, vocabUnit) {

  var tn = 'voc_added_template';
  var template = HtmlService.createTemplateFromFile(tn);
  template.firstName=getData(si).firstName;
  template.book=vocabUnit[0];
  template.lesson=vocabUnit[1];
  template.part=vocabUnit[2];
  var emailText = template.evaluate().getContent();
  var subject = "Book "+vocabUnit[0]+" chapter "+vocabUnit[1]+" part "+vocabUnit[2]+" added to Ankiweb - 第"+vocabUnit[1]+"課第"+vocabUnit[2]+"部分加好了";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}

function sendReminder0(si){
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"! Remember me? \u{1F643}\n"+
          "Don't forget you have all the textbook flashcards "+
          "with examples, images and sound\n"+
          "just one click away \u{1F609}\u{1F447}\n"+
          "https://ankiweb.net/decks/"

  if (lineId != null){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "Remember me? 🙃"
    var msgText = msgText.replace(' 🙃', "")
    var msgText = msgText.replace('sound\n', "sound ")
    var msgText = msgText.replace(' 😉👇', "!:")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, "reminder0", type);
}

function sendWReport(si, data){
  var lineId = getData(si).lineId
  var report = data[1]
  var msgText= "Hi "+getData(si).firstName+"!\n"+
          "Last week you spent "+report['time']+" reviewing "
  if (report['tbWords']>0){msgText=msgText+report['tbWords']+" words from "+report['chaps']+" chapters 📚 "}
  if (report['otbWords']>0){msgText=msgText+"and "+report['otbWords']+" words from outside the textbook 🌄"}
  if (report['top'].length >0) {
    msgText=msgText+"\n\n🚩 Difficult textbook words:"
    report['top'].forEach(
      w => msgText=msgText+"\n"+w[0]+" (book "+w[1][0]+" chapter "+w[1][1]+")"
    )
    }
  msgText=msgText+"\n\nGood job! 加油! 💪"

  if (lineId != null){ pushMsg(lineId, msgText); type='line' }

  else {
    var subject = "Your weekly report 📄"
    var msgText = msgText.replace(/(📚 |🚩 | 💪| 🌄)/g, "")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, data[0], type);
}

function testWreport(){
  data=[
    'weekly220117', {'tbWords': 37, 'otbWords': 28, 'reviews': 162, 'top': [['浴室', [1, 11]], 
['客廳', [1, 11]], ['帶', [1, 9]], ['租', [1, 11]], ['超市', [1, 11]], ['再', [1, 11]], ['走路', [1, 11]], ['套房', [1, 11]], ['空', [1, 11]], ['就', [1, 11]]], 'time': 'about 1 hour', 'chaps': 4}
  ]
  sendWReport(3, data)
}

function sendCustom(si) {
  var tn = 'custom_template';
  var template = HtmlService.createTemplateFromFile(tn);
  template.firstName=getData(si).firstName;
  var emailText = template.evaluate().getContent();
  var subject = "MTC flashcards - email not activated";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}

