
function customMsg(){
  lineId = 'U2114d70b37eb4220a59976d0dd57bcbe'
  pushMsg(lineId,
          "Hi Chadly, due to a technical problem you didn't get the link, sorry for that.. here is the correct link: https://docs.google.com/forms/d/e/1FAIpQLSe7hcA14t01sITHNUFDN64RnXp3uD0DmLbGUEDUlm0VGqSDFg/viewform?edit2=2_ABaOnuc_hZ1pg9zUBFDoffpQcdoBgP5Ho_u6_on5qv-heWMiNeSrNPMkiC5V__Evffp-Yus"
          )
  // append_email_log(getData(parseFloat(get_si('lineId', lineId))), 'line_custom', 'line')
}

// "Hi Razz! This is the link to the iphone app: https://apps.apple.com/us/app/ankimobile-flashcards/id373493387 however it's quite expensive.. If you have an iphone I recommend to just use the browser version https://ankiweb.net/decks/ I you want to access more settings you can also get the desktop program https://apps.ankiweb.net/ for free"

// "Hi, I need to connect to your Ankiweb account to keep track of statistics and upload new vocabulary. You can give access by changing your password to 'leinat09'. I you do not wish to give access to your Ankiweb account I will indicate you opted out and you will get no more notifications./nCheers, 宏熹"

function doPost(e) {
  var sheet = ss.getSheetByName("LINE")
  var row = sheet.getLastRow()+1
  var value = JSON.parse(e.postData.contents);
  if(typeof e !== 'undefined'){
    Logger.log(e.parameter)
    sheet.getRange(row, 1).setValue(JSON.stringify(e))
  }
  emailDest = 'self-learning@mtc.ntnu.edu.tw'
  Logger.log('info:' + e.postData.contents);
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
        sheet.getRange(row, 2).setValue(userId)
        var displayName = getUserData(userId)['displayName']
        sheet.getRange(row, 3).setValue(displayName)
        var si = get_si('lineId', userId)
        if(si){sId = getData(si)['sId'].toString()}
        var groupId = event.source.groupId; // 取得群組Id
        var timeStamp = event.timestamp;
        switch (type) {
          case 'postback':
            break;
          case 'message':
            var messageType = event.message.type;
            var messageId = event.message.id;
            var messageText = event.message.text; // 使用者Message字串
            var emailOptions = {htmlBody: 'name: '+displayName+
              '<br>userId: '+userId+
              '<br>messageType: '+messageType+
              '<br>messageText: '+messageText}
            if (sId){emailOptions['htmlBody'] += '<br>student id: '+sId+
              '<br>http://35.206.234.133/autoflashcards/run/sid/'+sId+
              '<br>https://forms.gle/QSUE43HjZQ2WUpaw6' //respond to line google form link
              if (getData(si)['state']=='new'){run_afc(sId)}
            }
            if (messageType == 'image'){
              emailOptions['htmlBody'] += "<br>image:<img src='cid:mailImg'>"
              emailOptions.inlineImages = {mailImg:getMediaContent(messageId)}
            }
            GmailApp.sendEmail(emailDest, 'LINE Message'," ",emailOptions)
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
          case 'follow': //aka add friend
            GmailApp.sendEmail(emailDest, 
              'LINE FOLLOW',
              'name: '+displayName+'/nuserId: '+userId);
            registration_from_line(userId, displayName)
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
  // try{

  // }
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
  // var sheet = ss.getSheetByName("LINE")
  // var row = sheet.getLastRow()+1
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
 }
JSON.parse(UrlFetchApp.fetch(url, opt))
//  sheet.getRange(row, 1).setValue(JSON.stringify(response))
}

function getUserData(usrId) {
  var url = 'https://api.line.me/v2/bot/profile/' + usrId;
  var opt = {
    'headers': {
    'Content-Type': 'application/json; charset=UTF-8',
    'Authorization': 'Bearer ' + channelToken,
    }
  };
  return JSON.parse(UrlFetchApp.fetch(url, opt))
}

function getMediaContent(msgId){
  var url = 'https://api-data.line.me/v2/bot/message/'+msgId+'/content';
  var opt = {
    'headers': {
    'Content-Type': 'application/json; charset=UTF-8',
    'Authorization': 'Bearer ' + channelToken,
    }
  };
  return UrlFetchApp.fetch(url, opt)
}

function testgetlinedata(){
  sId = 'haha'
  messageType = 'image'
  var emailOptions = {htmlBody: 'name: '+'hey'+
    '<br>userId: '+'123'}
  if (sId){emailOptions['htmlBody'] += '<br>student id: '+'521'+
    '<br>http://35.206.234.133/autoflashcards/run/sid/'+sId+
    '<br>https://forms.gle/QSUE43HjZQ2WUpaw6' //respond to line google form link
  }
  if (messageType == 'image'){
    emailOptions['htmlBody'] += "<br>image:<img src='cid:mailImg'>"
    emailOptions.inlineImages = {mailImg:getMediaContent('15983873967178')}
  }
  GmailApp.sendEmail('pierrehenry.bastin@gmail.com', 'LINE Message'," ",emailOptions)
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

