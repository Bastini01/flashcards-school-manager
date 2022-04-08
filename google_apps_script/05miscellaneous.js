var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18')
var dataSheet = ss.getSheetByName("Form Responses 1")
var clSheet = ss.getSheetByName("class")
var teSheet = ss.getSheetByName("teacher")


function seeRowsData(){
  // var ss = SpreadsheetApp.openById('1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18');
  // // var ss = SpreadsheetApp.getActiveSpreadsheet();
  // var dataSheet = ss.getSheetByName("Form Responses 1");
  var dataRange = dataSheet.getRange(2, 1, dataSheet.getLastRow() - 1, dataSheet.getLastColumn());
  Logger.log(getRowsData(dataSheet,dataRange));
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
  // var ss = SpreadsheetApp.getActiveSpreadsheet();
  // var dataSheet = ss.getSheetByName("Form Responses 1");
  // var clSheet = ss.getSheetByName("class");
  // var teSheet = ss.getSheetByName("teacher");
  var classes = []
  for (var i = 2; i < dataSheet.getLastRow(); ++i){
    cl=dataSheet.getRange(i, 6).getValue()
    if(typeof cl != 'string'){cl=cl.toString()}
    // Logger.log(classes)
    // if (!(cl in classes)){classes.push(cl)}
    if (!classes.includes(cl)){classes.push(cl)}

    // Logger.log(!(cl in classes))
    
  }
  clss=classes.map(x => [x])
  Logger.log(clss)
  r=clSheet.getRange(2,1,clss.length)
  r.setValues(clss)
}

function fill_class_data_teacher(){
  // var ss = SpreadsheetApp.getActiveSpreadsheet();
  // var dataSheet = ss.getSheetByName("Form Responses 1");
  // var clSheet = ss.getSheetByName("class");
  // var teSheet = ss.getSheetByName("teacher");
  var teachersClass = teSheet.getRange(1, 5, teSheet.getLastRow()).getValues()
  tc=teachersClass.map(x => x[0].toString())
  Logger.log(tc)
  // var classes = clSheet.getRange(2, 1, clSheet.getLastRow()).getValues()
  for (var i = 2; i < clSheet.getLastRow(); ++i){
    cl=clSheet.getRange(i, 1).getValue().toString()
    Logger.log(cl)
    // if(typeof cl != 'string'){cl=cl.toString()}
    // Logger.log(classes)
    // if (!(cl in classes)){classes.push(cl)}
    if (tc.includes(cl)){
      indx=tc.indexOf(cl)      
      clSheet.getRange(i, 2).setValue(
        teSheet.getRange(indx+1, 1).getValues()
      )
    }

    // Logger.log(!(cl in classes))
    
  }

}

//Logger.log('logging?');