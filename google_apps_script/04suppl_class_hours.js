var shss = SpreadsheetApp.openById('1GZGz8N4a-r125qxtlcRUvlNn29OxS_0VJGvV9d8I0SE')
var shSheet = shss.getSheetByName("sup_hours_log")

function last_submission(studentId, row){
  var sId = parseFloat(studentId)
  var hist = shSheet.getRange(380, 2, row-380, 5).getValues() 
  for (var i = hist.length-1; i > 0 ; i--) { 
    if (sId == hist[i][0] && hist[i][4]!='-'){return hist[i][1]}
  }
}

function add_supp_hours(studentId, h){
  var form = FormApp.openById('1KC3Fts68-WIBwva0Ox5O6OBWtqsdNWLLuaifCMzHv5s')
  itemResponses=[
    form.getItemById(922445849).asTextItem().createResponse(studentId),
    form.getItemById(2138974802).asTextItem().createResponse(h),
    form.getItemById(1826756305).asTextItem().createResponse("自動化字卡"),
    form.getItemById(1119369095).asTextItem().createResponse("自動化字卡")
  ]

  resp = form.createResponse()
  itemResponses.forEach(
    w => resp.withItemResponse(w)
  )
  resp = resp.submit()
  // items=form.getItems()
  // items.forEach(
  //   w => Logger.log(w.asTextItem().getId()+w.asTextItem().getTitle())
  // )

}

function handleSuppHoursSubmission(e){ //triggererd from supplementary hours submission form
  var resp = e.values
  var row = e.range['rowStart']

  if (resp[3]=="自動化字卡"){
    shSheet.getRange(row, 6).setValue(resp[2])
    send_to_mtc(resp, resp[2])
  }
  
  else {
    var lastSubmission = last_submission(resp[1], row)
    if (!lastSubmission){
      if (resp[2]<200){shSheet.getRange(row, 6).setValue('-')}
      else if (resp[2]<400){
        shSheet.getRange(row, 6).setValue(1)
        send_to_mtc(resp, 1, false)
        }
      else {
        shSheet.getRange(row, 6).setValue(2)
        send_to_mtc(resp, 2, false)
      }
    }
    else{
      if (resp[2]-lastSubmission<200){shSheet.getRange(row, 6).setValue('-')}
      else if (resp[2]-lastSubmission<400){
        shSheet.getRange(row, 6).setValue(1)
        send_to_mtc(resp, 1, false)
      }
      else {
        shSheet.getRange(row, 6).setValue(2)
        send_to_mtc(resp, 2, false)
      }
    }
  }
}

function send_to_mtc(resp, hours, auto=true){
  var h = hours.toString()
  
  msgText="陳小姐您好,\n\n"+
      "學生號 "+resp[1]+" 以字卡app自主學習獲得了 "+h+" 個小時必修時數.\n\n"
  if (auto){
    msgText=msgText+"其資料以MTC自動化字卡系統直接從學生的APP數據讀取."
  }
  else {
    msgText=msgText+"總共複習次數: "+resp[2]+"\n"+
    "已增加生詞量: "+resp[3]+"\n"+
    "已學會生詞量: "+resp[4]
  }
  msgText=msgText+"\n\n謝謝"
  
  GmailApp.sendEmail(
    'mtcmtc@ntnu.edu.tw',
    // 'pierrehenry.bastin@gmail.com',      
    '自學時數: '+resp[1]+' - '+h+'小時',
    msgText
    )
}

