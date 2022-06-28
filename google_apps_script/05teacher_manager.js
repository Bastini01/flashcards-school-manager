function getTeacherNumber(teacherName){
    var nameList = teSheet.getRange(1, 4, teSheet.getLastRow(), 1).getValues().flat()
    return teSheet.getRange(nameList.indexOf(teacherName)+1 , 1).getValue()
  }
  
function get_teacherList(){
  var teacherList = teSheet.getRange(2, 1, teSheet.getLastRow(), 4).getValues()
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
  var tiss = SpreadsheetApp.openById('1MHz-K8-NxgwrfMw3DvNrbuKcXSeewJyRjsA5W6GkhT8').getSheets()
  levelFilter = ["當代中文課程（一）", "當代中文課程（二）", "當代中文課程（三）"]
  previewSheet = tiss[1]
  lls = tiss[tiss.length-2]
  tms = tiss[tiss.length-1] //teacher email sheet

  ll = lls.getRange(2, 1, lls.getLastRow(), lls.getLastColumn()).getValues()
  registeredTeachers = get_teacherList().map(item => item[0])

  ll = ll.filter(item => levelFilter.includes(item[8]))
  ll = ll.filter(item => !(item[8] == levelFilter[2] && item[9]>6)) //remove classes above book3 unit 6
  ll = ll.filter(item => !registeredTeachers.includes(item[0]))

  ll.sort((a,b) => (a[1] > b[1]) ? 1 : ((b[1] > a[1]) ? -1 : 0))
  ll = ll.map(item => [item[0], item[1]])
  
  ll = [...new Set(ll.flat())]
  ll1 = []; while (ll.length > 0) ll1.push(ll.splice(0, 2))
  
  teacherEmails = tms.getRange(2, 1, tms.getLastRow(), 4).getValues()
  idx = teacherEmails.map(item => item[0]).flat()
  ll1.forEach(function(e){
    if (idx.indexOf[e[0]] == -1){e[2] = "-"}
    else {e[2] = teacherEmails[idx.indexOf(e[0])][3]}
  })

  ll1 = ll1.map(item => [item[0], item[2], item[1]])

  // Logger.log(ll1)
  // previewSheet.getRange(1, 1, previewSheet.getLastRow(), 3).clear()
  previewSheet.getRange(1, 1, ll1.length, 3).setValues(ll1)
}

