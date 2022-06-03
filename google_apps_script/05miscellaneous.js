var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18')
var dataSheet = ss.getSheetByName("Form Responses 1")
var clSheet = ss.getSheetByName("class")
var teSheet = ss.getSheetByName("teacher")



function seeRowsData(){
  var dataRange = dataSheet.getRange(2, 1, dataSheet.getLastRow() - 1, dataSheet.getLastColumn());
  Logger.log(getRowsData(dataSheet,dataRange));
}

function current_term(){
  year = today.getFullYear().toString().slice(2,4)
  if (today.getMonth() <=1 || today.getMonth()+1 == 11) {return year+"winter"}
  else if (today.getMonth() <=4) {return year+"spring"}
  else if (today.getMonth() <=7) {return year+"summer"}
  else {return year+"fall"}
}

function testhandleDesktopRequest(){
  var rq = '{"0":{"studentIndex":2,"statusUpdate":"connected","chapterUpdate":null,"emailTemplate":"connectSuccess"},"1":{"studentIndex":3,"statusUpdate":"wrongPassw","chapterUpdate":"Chapter1","emailTemplate":"wrongPassw"},"2":{"studentIndex":2,"statusUpdate":"upToDate","chapterUpdate":null,"emailTemplate":"newChaptAdded"}}';
  result=handleDesktopRequest(rq);
  Logger.log(result);
}

function tstingFunction() {
  var list=['d','f','g']; list = list.slice(-5); Logger.log(list)
}

function test220331(){
  var time1 = new Date()
  var sec1 = time1.getSeconds()
  var msec1 = time1.getMilliseconds()
  Logger.log(sec1); Logger.log(msec1)
  Utilities.sleep(500)
  var time2 = new Date()
  Logger.log(time2.getSeconds()); Logger.log(time2.getMilliseconds())
  var dif = Math.abs(time2-time1)
  Logger.log(dif)
  if (dif<1000){Utilities.sleep(700-dif)}
  Logger.log(new Date().getSeconds()); Logger.log(new Date().getMilliseconds())
}

function fill_class_data_class(){
  var classes = []
  for (var i = 2; i < dataSheet.getLastRow(); ++i){
    cl=dataSheet.getRange(i, 6).getValue()
    if(typeof cl != 'string'){cl=cl.toString()}
    if (!classes.includes(cl)){classes.push(cl)}   
  }
  clss=classes.map(x => [x])
  Logger.log(clss)
  r=clSheet.getRange(2,1,clss.length)
  r.setValues(clss)
}

function fill_class_data_teacher(){
  var teachersClass = teSheet.getRange(1, 5, teSheet.getLastRow()).getValues()
  tc=teachersClass.map(x => x[0].toString())
  Logger.log(tc)
  for (var i = 2; i < clSheet.getLastRow(); ++i){
    cl=clSheet.getRange(i, 1).getValue().toString()
    Logger.log(cl)
    if (tc.includes(cl)){
      indx=tc.indexOf(cl)      
      clSheet.getRange(i, 2).setValue(
        teSheet.getRange(indx+1, 1).getValues()
      )
    }
  }

}

function getTeacherNumber(teacherName){
  var nameList = teSheet.getRange(1, 4, teSheet.getLastRow(), 1).getValues().flat()
  return teSheet.getRange(nameList.indexOf(teacherName)+1 , 1).getValue()
}

function updateTeacherList(){ //triggered once a month or manually
  var teacherList = teSheet.getRange(2, 2, teSheet.getLastRow(), 3).getValues()
  teacherList = teacherList.filter(item => item[0].includes('@'))
  teacherList = teacherList.map(item => item[2]).sort()
  teacherList.push("Other - 其他")
  Logger.log(teacherList)
  var updateForm = FormApp.openById('1XsN8z4uueZH0HZlu69sviR70yJrxwo9LBPvN47sHXF0')
  updateForm.getItemById(130655611).asListItem().setChoiceValues(teacherList)
  form.getItemById(919431551).asListItem().setChoiceValues(teacherList)
}

