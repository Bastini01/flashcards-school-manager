var channelToken = "xyy6eUsoQBfzVV4IGe1BKguVCgJY5N31Kv9Dmc4+OZTkYOLT6/ukK0CpUa8I/S2zhlD1DTcUfHppzLxLYo6ueSUThuHjUBpg6COJVrDzH9CoaNxX2KgWivGx6K4XtfOZoUi51RvjrAccIvDbHpGeJwdB04t89/1O/w1cDnyilFU="

function customMsg(){
  pushMsg('U02e268a357d377f429911a1fd87c52e4',
          'test'
          )
}

function doPost(e) {
  var sheet = ss.getSheetByName("LINE");
  if(typeof e !== 'undefined'){
    Logger.log(e.parameter);
    sheet.getRange(sheet.getLastRow()+1, 1).setValue(JSON.stringify(e));
  }
  emailDest = 'self-learning@mtc.ntnu.edu.tw'
  Logger.log('info:' + e.postData.contents);
  var value = JSON.parse(e.postData.contents);
  // Logger.log('I got here!');
  try {
    var events = value.events;
    if (events != null) {
      for (var i in events) {
        var event = events[i];
        var type = event.type;
        var replyToken = event.replyToken; // 要回復訊息 reToken
        var sourceType = event.source.type;
        // var sourceId = LineHelpers.getSourceId(event.source);
        var userId = event.source.userId; // 取得個人userId
        var groupId = event.source.groupId; // 取得群組Id
        var timeStamp = event.timestamp;
        switch (type) {
          case 'postback':
            break;
          case 'message':
            var messageType = event.message.type;
            var messageId = event.message.id;
            var messageText = event.message.text; // 使用者Message字串
            GmailApp.sendEmail(emailDest, 
              'LINE Message',
              'userId: '+userId+
              '<br>messageType: '+messageType+
              '<br>messageText: '+messageText);
            break;
          case 'join':
            GmailApp.sendEmail(emailDest, 
              'LINE join',
              'userId: '+userId);
            break;
          case 'leave':
            GmailApp.sendEmail(emailDest, 
              'LINE leave',
              'userId: '+userId);
            break;
          case 'memberLeft':
            GmailApp.sendEmail(emailDest, 
              'LINE memberLeft',
              'userId: '+userId);
            break;
          case 'memberJoined':
            GmailApp.sendEmail(emailDest, 
              'LINE memberJoined',
              'userId: '+userId);
            break;
          case 'follow':
            GmailApp.sendEmail(emailDest, 
              'LINE FOLLOW',
              'userId: '+userId);
            break;
          case 'unfollow':
            GmailApp.sendEmail(emailDest, 
              'LINE UNFOLLOW',
              'userId: '+userId);
            break;
          default:
            break;
        }
        
      }
    }
  } catch(ex) {
    Logger.log(ex);
  }
}

function replyMsg(replyToken, userMsg) { // doesn't work
  var url = 'https://api.line.me/v2/bot/message/reply';
  var opt = {
        'headers': {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer ' + channelToken,
          },
        'method': 'post',
        'payload': JSON.stringify({
          'replyToken': replyToken,
          'messages': [{'type': 'text', 'text': userMsg}]
          })
        };
  UrlFetchApp.fetch(url, opt);
}

function testreplyMsg(){
  replyMsg('95798fb998314685a0c55912aa243af0',"retest");
}

function pushMsg(usrId, message) {
  var url = 'https://api.line.me/v2/bot/message/push';
  var opt = {
    'headers': {
    'Content-Type': 'application/json; charset=UTF-8',
    'Authorization': 'Bearer ' + channelToken,
  },
  'method': 'post',
  'payload': JSON.stringify({
    'to': usrId,
    'messages': [{'type': 'text', 'text': message}]
  })
 };
 UrlFetchApp.fetch(url, opt);
}

function getUserData(usrId) {
  var url = 'https://api.line.me/v2/bot/profile/' + usrId;
  var opt = {
    'headers': {
    'Content-Type': 'application/json; charset=UTF-8',
    'Authorization': 'Bearer ' + channelToken,
    }
  };
  return JSON.parse(UrlFetchApp.fetch(url, opt));
}

function get_all_user_data(){
  var sheet = ss.getSheetByName("LINE");
  for (let i = 1; i <= sheet.getLastRow(); i++){
    try{
    // Logger.log(i)
    // usrId = sheet.getRange(i,1).getValue().split("userId")[1].slice(5, 38)
    // displayName = getUserData(usrId)["displayName"]
    // sheet.getRange(i,3).setValue(displayName+": "+usrId)
    // Logger.log(displayName+": "+usrId)
    displayName = sheet.getRange(i,3).getValue().split(": ")[0]
    usrId = sheet.getRange(i,3).getValue().split(": ")[1]
    sheet.getRange(i,2).setValue(displayName)
    sheet.getRange(i,3).setValue(usrId)

    }
    catch{}
  }
}

