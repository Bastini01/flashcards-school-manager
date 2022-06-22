function getTeacherNumber(teacherName){
    var nameList = teSheet.getRange(1, 4, teSheet.getLastRow(), 1).getValues().flat()
    return teSheet.getRange(nameList.indexOf(teacherName)+1 , 1).getValue()
  }
  
function get_teacherList(){
  var teacherList = teSheet.getRange(1, 2, teSheet.getLastRow(), 4).getValues()
  return teacherList.filter(item => item[1].includes('@'))
}

function updateTeacherList(){ //triggered once a month or manually
  teacherList = get_teacherList().map(item => item[3]).sort()
  teacherList.push("Other - 其他")
  Logger.log(teacherList)
  var updateForm = FormApp.openById('1XsN8z4uueZH0HZlu69sviR70yJrxwo9LBPvN47sHXF0')
  updateForm.getItemById(130655611).asListItem().setChoiceValues(teacherList)
  form.getItemById(919431551).asListItem().setChoiceValues(teacherList)
}

function send_teacher_promotion(){ //triggered (once per term or) manually 
  teacherList = get_teacherList()
  term=current_term('zh')
  qrcode = DriveApp.getFileById('1UCzhSXItnBw9M01gNmZbQUVKilqlXTbZ1PMrHYcGnUQ').getBlob()
  for (i in teacherList){
  t = teacherList[i]
  var templateName = 'teacher_reminder';
  var template = HtmlService.createTemplateFromFile(templateName);
  template.teacherLN=t[3].charAt(0);
  var emailText = template.evaluate().getContent();
  var subject = "「MTC自動化字卡」20"+term.slice(0,2)+"年"+term.charAt(2)+"季推動計畫"
  // GmailApp.sendEmail(t[0], subject," ", {htmlBody: emailText, cc: 'shuhuafang@mtc.ntnu.edu.tw', attachments: [qrcode]})
  // GmailApp.sendEmail('pierrehenry.bastin@gmail.com', subject," ", {htmlBody: emailText, attachments: [qrcode]})
  append_email_log('teacher'+t[2], templateName);
  }
}

function prepare_teacher_invites() {
  var teacherInviteSs = SpreadsheetApp.openById('1MHz-K8-NxgwrfMw3DvNrbuKcXSeewJyRjsA5W6GkhT8')
  levelFilter = ["當代中文課程（一）", "當代中文課程（二）", "當代中文課程（三）"]
  previewSheet = teacherInviteSs.getSheets()[1]
  latestListSheet = teacherInviteSs.getSheets()[-1]
  latestList = latestListSheet.getRange(2, 1, latestListSheet.getLastRow(), latestListSheet.getLastColumn()).getValues()
  previewSheet.getRange(1, 1, previewSheet.getLastRow(), 2).clear()
  registeredTeachers = get_teacherList().map(item => item[0])
  ll = latestList.filter(item => item[8] in levelFilter)
  ll = ll.filter(item => item[0] in registeredTeachers)
  previewSheet.getRange(1, 2, ll.leng)
}