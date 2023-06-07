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
  send_to_mtc(studentId, h)
}

function send_to_mtc(studentId, h){
  msgText="陳小姐您好,\n\n"
  msgText=msgText+"學生號 "+studentId+" 以字卡app自主學習獲得了 "+h+" 個小時必修時數.\n\n"
  msgText=msgText+"其資料以MTC自動化字卡系統直接從學生的APP數據讀取."
  msgText=msgText+"\n\n謝謝"
  
  GmailApp.sendEmail(
    'mtcmtc@ntnu.edu.tw',
    '自學時數: '+studentId+' - '+h+'小時',
    msgText
    )
}

