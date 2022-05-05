function customSender () {
  target= []
  // target = autoArray()
  for (var i = 0; i < target.length; i++){
    Logger.log(target[i]+", "+ getData(target[i]).email+", "+ getData(target[i]).firstName)
    // sendWrongPasswordMail(target[i])
    // sendChapterUpdateMail(target[i], [1,9,2])
    // sendActivated(target[i])
    // sendNotActivated(target[i])
    // sendCustom3(target[i])
    // sendReminder0(target[i])
    // sendAnkiInstructions(target[i])
    // sendTermUpdate(target[i])
    // sendTermUpdateReminder(target[i])
  }
  
}

function autoArray(){
  start=8
  end=132
  except = [] //[14, 15, 16, 18, 25, 27, 32, 41, 44, 54, 59, 65, 67, 69, 83, 88, 94, 96, 98, 100, 101]
  arr = [...Array(end - start + 1).keys()].map(x => x + start)
//REMOVE STUDENTS FROM MAILING LIST ACCORDING TO STATUS FILTER
  for (var i = 0; i < arr.length; i++){
  if (getData(arr[i])['state'].slice(0,1)=='t') {except.push(i+start)}
  }
  Logger.log(except)
  for (var i = 0; i < except.length; i++){
    var index = arr.indexOf(except[i])
    if (index > -1) {arr.splice(index, 1)}
  }
  Logger.log(arr)
  return arr
}

function fillTemplateA(si, template) {
  template.firstName=getData(si).firstName;
  template.emailAddress=getData(si).email;
  template.ankiwebPassword=getData(si).pw;
  return template.evaluate().getContent();
}

function append_email_log(studentIndex, templateName, type){
  if (type==null){type='gmail'}
  var dataRange = emailLog.getRange(emailLog.getLastRow()+1, 1, 1, 5);
  var values = [[today, getData(studentIndex).sId, getData(studentIndex).firstName, templateName, type]];
  dataRange.setValues(values);
}

function sendRegReminder(si){
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
      "🚩It seems your registration is incomplete.\n"+
      "If you wish to use MTC Automated flashcards and get supplementary hours please fill in the form through the link in the message above.\n"+
      "If you have any questions just send a message ;)"
  if (lineId){pushMsg(lineId, msgText); type='line'}
  else{
  var subject = "🚩MTC Automated flashcards registration"
    // var msgText = msgText.replace('🙏', " :)")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }
  append_email_log(si, "registration_reminder", type);
}

function sendOnboarding(si){
  var tn = 'onboarding-template';
  var template = HtmlService.createTemplateFromFile(tn);
  var emailText = fillTemplateA(template);
  var subject = "MTC automated flashcards instructions - MTC自動化字卡說明";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}

function sendAnkiInstructions(si){
  var lineId = getData(si).lineId
  var email = getData(si).email
  var password = getData(si).pw
  var msgText="Hi "+getData(si).firstName+"!\n"+
          "Thank you for registering,\n"+
          "next please create an Ankiweb account with\n"+
          "USERNAME: "+email+"\n"+
          "PASSWORD: 👉"+password+"👈\n"+
          "Once you have activated the account please let us know by answering this message!\n"+
          "https://ankiweb.net/account/register"

  pushMsg(lineId, msgText); type='line'
  
  append_email_log(si, "AnkiInstructions", type);
}

function sendTermUpdate(si){
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
          "Ready for the new term?\n"+
          "Please let us know if you continue and what your new class is🙏\n"+
          "You might need to ask your teacher for the class number\n"+
          "Thank you!\n"+
          "https://forms.gle/9BhRn2kbZdKMJR1X8"
  if (lineId){pushMsg(lineId, msgText); type='line'}
  else{
  var subject = "New term class update!"
    var msgText = msgText.replace('🙏', " :)")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }
  append_email_log(si, "termUpdate", type);
}

function sendTermUpdateReminder(si){
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
          // "I just noticed you're already registered.\n"+
          "If you want to continue getting new flashcards please fill in the form below with your updated class data. "+ 
          "You might need to ask your teacher for the class number\n"+
          "Thank you!\n"+
          "https://forms.gle/9BhRn2kbZdKMJR1X8"
  if (lineId){
  pushMsg(lineId, msgText); type='line'
    }
  else{
  var subject = "Already registered"
    // var msgText = msgText.replace('🙏', " :)")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }
  append_email_log(si, "termUpdateReminder", type);
}

function sendActivated(si) {
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
          "Connection to your Ankiweb account was successful, you can now start reviewing👨‍🏫\n"+
          "https://ankiweb.net/decks/"

  if (lineId){
  pushMsg(lineId, msgText); type='line'
  append_email_log(si, 'activated_template', type);
  }
  else{

  var tn = 'activated_template';
  var template = HtmlService.createTemplateFromFile(tn);
  template.firstName=getData(si).firstName;
  var emailText = template.evaluate().getContent();
  var subject = "MTC automated flashcards activated - MTC自動化字卡建立成功";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn, 'gmail');
  }
}

function sendWrongPassword(si) {
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
          "🚩We couldn't connect to your Ankiweb account\n"+
          "Please change your Ankiweb password to:\n"+
          getData(si).pw+"\n"+
          "Your username must be: "+getData(si).email+
          "https://ankiweb.net/account/settings"

  if (lineId){
  pushMsg(lineId, msgText); type='line'
  append_email_log(si, 'wrong_password_template', type);
  }
  else{
  var tn = 'wrong_password_template';
  var template = HtmlService.createTemplateFromFile(tn);
  var emailText = fillTemplateA(si,template);
  var subject = "MTC automated flashcards password error - MTC自動化字卡錯誤";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn, 'gmail');
  }
}

function sendNotActivated(si) {
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
          "It seems your Ankiweb account is not activated yet, you still need to validate your email.\n"+
          "Please check your mail for an 'email verification' mail from Ankiweb and click the link inside it to verify your email address.\n"
    if (lineId){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "Ankiweb email not yet validated"
    // var msgText = msgText.replace(' 🙃', "")
    // var msgText = msgText.replace('sound\n', "sound ")
    // var msgText = msgText.replace(' 😉👇', "!:")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, "notAcivated", type);
}


function sendWrongForm(si) {
  var tn = 'wrong_form_template';
  var template = HtmlService.createTemplateFromFile(tn);
  var emailText = fillTemplateA(si,template);
  var subject = "MTC automated flashcards form error - MTC自動化字卡錯誤";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn, 'gmail');
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
          "Don't forget you have the textbook flashcards "+
          "with examples, images and sound\n"+
          "just one click away \u{1F609}\u{1F447}\n"+
          "https://ankiweb.net/decks/"

  if (lineId){ pushMsg(lineId, msgText); type='line' }
  
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

function sendAccReport(si, data){
  d=data[1]
  var lineId = getData(si).lineId
  var msgText="Hi "+getData(si).firstName+"!\n"+
          "Already "+d['#Chapters']+" chapters this term.\n"+
          "🚩That's "+d['#Words']+" words in total. Should take about "+d['time']+" to review.\n\n"
          d['list'].forEach(
            w => msgText = msgText+"->Book "+w[0][0]+" chapter "+w[0][1]+":\n"+w[1]+" words ~"+w[2]+"\n"
          )
          msgText= msgText+"\nDon't wait until it's too much 😉\n"+
          "https://ankiweb.net/decks/"

  if (lineId){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "🚩 "+d['#Chapters']+" chapters to review"
    var msgText = msgText.replace('😉', ";)")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, data[0], type);
}

function sendCustom(si){
  var lineId = getData(si).lineId
  var msgText="考試"

  if (lineId){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "大考試加油!"
    var msgText = msgText.replace(' 😉👇', " ;) :")
    // var msgText = msgText.replace(' 🐯', "!:")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, "customCNY", type);

}

function sendCustom1(si){
  var lineId = getData(si).lineId
  var msgText=getData(si).firstName+" 你好,\n"+
          "If you haven't had it yet, good luck with the 大考試!\n"+
          "We just calculated this term it took students on average 17,5 minutes to review one chapter using Anki.\n"+
          "Reminder just in case you have some last minute reviewing to do \u{1F609}\u{1F447}\n"+
          "https://ankiweb.net/decks/"

  if (lineId){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "大考式加油!"
    var msgText = msgText.replace(' 😉👇', " ;) :")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, "customCNY", type);
}


function sendCustom2(si){
  var lineId = getData(si).lineId
  Logger.log(lineId)
  var msgText=getData(si).firstName+" 新年快樂! 🐯\n"+
          "Have fun during the holidays but don't forget all of your Chinese...\n"+
          "Wherever you are, reviewing a chapter just takes a few minutes \u{1F609}\u{1F447}\n"+
          "https://ankiweb.net/decks/"

  if (lineId){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "新年快樂! 🐯"
    var msgText = msgText.replace(' 😉👇', "!:")
    var msgText = msgText.replace(' 🐯', "!:")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, "customCNY", type);
}

function sendCustom3(si){
  var lineId = getData(si).lineId
  var msgText="Supplementary class hours for self-study:\n"+
          getData(si).firstName+" 你好\n"+
          "Good news! Starting this month you can get large group class hours for self-study with Anki.\n"+
          "How does it work? Just do your reviews, as soon as you reach an hour of study you will be notified and the time will be added to your attendance record automatically, you can get up to 8 hours/month.\n"+
          "Don't hesitate to share this news with your friends! ;)\n"+
          "https://ankiweb.net/decks/"

  if (lineId){ pushMsg(lineId, msgText); type='line' }
  
  else {
    var subject = "New: get supplementary class hours for self-study with Anki"
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, "customSuppClassHours", type);
}

function sendWReport(si, data){
  var lineId = getData(si).lineId
  Logger.log(lineId)
  var report = data[1]
  var msgText= "Hi "+getData(si).firstName+"!\n"
  if (report['reviews'] > 0){
     msgText=msgText+"Last week you spent "+report['time']+" reviewing "
  if (report['tbWords']>0){msgText=msgText+report['tbWords']+" words from "+report['chaps']+" chapters 📚 "}
  if (report['otbWords']>0){msgText=msgText+"and "+report['otbWords']+" words from outside the textbook 🌄"}
  if (report['top'].length >0) {
    msgText=msgText+"\n\n🚩 Difficult textbook words:"
    report['top'].forEach(
      w => msgText=msgText+"\n"+w[0]+" (book "+w[1][0]+" chapter "+w[1][1]+")"
    )
    }
  }
  else{
    msgText=msgText+"Don't forget to keep reviewing! 👨‍🏫 The more you wait the more time you'll spend"
    if (report['pending'] >0) {
    msgText=msgText+"\n\n🚩 Reviews pending:"
    report['pendingLearning'].slice(-5).forEach(
      w => msgText=msgText+"\n--> Book "+w[0][0]+" chapter "+w[0][1]+"\n"+(w[1]+w[2])+" reviews ~ "+w[3]
    )
    }
  }
  // if (report['completion'][0].length >0){
  //   msgText=msgText+"\n\nYou reviewed every word at least once for "+report['completion'][0].length.toString()+" chapters so far."
  // }
  if (report['completion'][1]){
    msgText=msgText+"\n\n🚩 Incomplete chapters:"
    report['completion'][1].forEach(
      w => msgText=msgText+"\n--> Book "+w[0][0]+" chapter "+w[0][1]+"\n"+w[1]+" words left ~"+w[2]+" minutes"
    )
  }
  msgText=msgText+"\n\n加油! 💪"
  if (report['reviews'] == 0){
  msgText=msgText+"\n\nhttps://ankiweb.net/decks/"
  }

  if (lineId){ pushMsg(lineId, msgText); type='line' }

  else {
    var subject = "Your weekly report 📄"
    var msgText = msgText.replace(/(📚 |🚩 | 💪| 🌄| 👨‍🏫|)/g, "")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, data[0], type);
}

function sendDReport(si, data){
  var lineId = getData(si).lineId
  var report = data[1]
  var msgText= "Hi "+getData(si).firstName+"!\n"
  if (report['reviews'] > 0){
          msgText=msgText+"Yesterday you spent "+report['time']+" reviewing "
  if (report['tbWords']>0){msgText=msgText+report['tbWords']+" words from "+report['chaps']+" chapters 📚 "}
  if (report['otbWords']>0){msgText=msgText+"and "+report['otbWords']+" words from outside the textbook 🌄"}
  // if (report['top'].length >0) {
  //   msgText=msgText+"\n\n🚩 Difficult textbook words:"
  //   report['top'].forEach(
  //     w => msgText=msgText+"\n"+w[0]+" (book "+w[1][0]+" chapter "+w[1][1]+")"
  //   )
  //   }
  }
  if (report['completion'][1].length >0){
    msgText=msgText+"\n\nSome chapters you didn't finish yet:"
    report['completion'][1].forEach(
      w => msgText=msgText+"\n--> Book "+w[0][0]+" chapter "+w[0][1]+"\n"+w[1]+" words left ~"+w[2]+"min."
    )
  }
  msgText=msgText+"\n\n加油! 💪"

  if (lineId){ pushMsg(lineId, msgText); type='line' }

  else {
    var subject = "Yesterday's reviews 📄"
    var msgText = msgText.replace(/(📚 |🚩 | 💪| 🌄| 👨‍🏫)/g, "")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, data[0], type);
}

function sendSuppHours(si, h, sh){
  var lineId = getData(si).lineId
  var tot = parseInt(h)+parseInt(sh)
  var msgText= "Hi "+getData(si).firstName+"!\n"+
        "You have earned "+h+" supplementary large group class hour(s) through flashcard self-study, it will appear in your attendance record shortly."
  if (sh!="0"){
    msgText=msgText+"\nThis month you have earned "+tot.toString()+" hours so far."
  }
  if (lineId){ pushMsg(lineId, msgText); type='line' }
  else {
  var subject = "You earned "+h+" supplementary class hour(s) for self-study"
  GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
  type='gmail'
  }
  append_email_log(si, "suppHours", type);
}

function sendTermProgressReport(si, data){
  var lineId = getData(si).lineId
  var report = data[1]
  var msgText= "Hi "+getData(si).firstName+"!\n"+
          "This term you reviewed "+report['time']+" chapters. Some of those weren't completed:"
  if (report['top'].length >0) {
    msgText=msgText+"\n\n🚩 Difficult textbook words:"
    report['top'].forEach(
      w => msgText=msgText+"\n"+w[0]+" (book "+w[1][0]+" chapter "+w[1][1]+")"
    )
    }
  msgText=msgText+"We recommend finishing reveiwing these chapters, then the app will make you practice the more difficult words"
  "\n\nGood job! 加油! 💪"

  if (lineId){ pushMsg(lineId, msgText); type='line' }

  else {
    var subject = "Your weekly report 📄"
    var msgText = msgText.replace(/(📚 |🚩 | 💪| 🌄)/g, "")
    GmailApp.sendEmail(getData(si).email,`=?UTF-8?B?${Utilities.base64Encode(Utilities.newBlob(subject).getBytes())}?=`,msgText);
    type='gmail'
  }

  append_email_log(si, data[0], type);
}

function testClassWeekly(){
  data=[
    'weekly220117', {'tbWords': 37, 'otbWords': 28, 'reviews': 162, 'top': [['浴室', [1, 11]], 
['客廳', [1, 11]], ['帶', [1, 9]], ['租', [1, 11]], ['超市', [1, 11]], ['再', [1, 11]], ['走路', [1, 11]], ['套房', [1, 11]], ['空', [1, 11]], ['就', [1, 11]]], 'time': 'about 1 hour', 'chaps': 4}
  ]
  // sendWReport(3, data)
  Logger.log(data[1]['top'][3].length.toString())
  for (const [key, value] of Object.entries(data[1])) {
    var a=key+value
  Logger.log(a);
  // Logger.log(value);
}

}

function sendClassWeekly(data){
  var template = HtmlService.createTemplateFromFile('classWeekly_template');
  template.name=data['teacherName'][0];
  var emailText = data['htmlReport'] + template.evaluate().getContent();
  subject= "「MTC自動化字卡」- 班號: "+data['class']+" - 每周報告"
  GmailApp.sendEmail(data['teacherEmail'], subject," ", {htmlBody: emailText, cc: 'shuhuafang@mtc.ntnu.edu.tw'});
  // GmailApp.sendEmail("pierrehenry.bastin@gmail.com", subject," ", {htmlBody: emailText});

  var dataRange = emailLog.getRange(emailLog.getLastRow()+1, 1, 1, 5);
  var values = [[today, data['teacherId'], data['teacherName'], "cw"+data['class']+data['timeFrame'], 'gmail']];
  dataRange.setValues(values);
}


function sendCustomHtml(si) {
  var tn = 'custom_template';
  var template = HtmlService.createTemplateFromFile(tn);
  template.firstName=getData(si).firstName;
  var emailText = template.evaluate().getContent();
  var subject = "MTC flashcards - email not activated";
  GmailApp.sendEmail(getData(si).email, subject," ", {htmlBody: emailText});
  append_email_log(si, tn);
}