function seeRowsData(){
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var dataSheet = ss.getSheetByName("Form Responses 1");
  var dataRange = dataSheet.getRange(2, 1, dataSheet.getLastRow() - 1, dataSheet.getLastColumn());
  Logger.log(getRowsData(dataSheet,dataRange));
}

function testhandleDesktopRequest(){
  var rq = '{"0":{"studentIndex":2,"statusUpdate":"connected","chapterUpdate":null,"emailTemplate":"connectSuccess"},"1":{"studentIndex":3,"statusUpdate":"wrongPassw","chapterUpdate":"Chapter1","emailTemplate":"wrongPassw"},"2":{"studentIndex":2,"statusUpdate":"upToDate","chapterUpdate":null,"emailTemplate":"newChaptAdded"}}';
  result=handleDesktopRequest(rq);
  Logger.log(result);
}

function tstingFunction() {
  var today = new Date();
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var dataSheet = ss.getSheetByName("Form Responses 1");
  var emailLog = ss.getSheetByName("Email log");
  var dataRange = dataSheet.getRange(dataSheet.getLastRow(), 1, 1, dataSheet.getLastColumn());
  headers = getHeaders(dataSheet, dataRange, 1);
 //set default Anki password
  var emailAdress = dataSheet.getRange(dataSheet.getLastRow(),2).getValue();
  var t='11-2new';
  var s=t.split('-')[1];
  Logger.log(s);
}

//Logger.log('logging?');