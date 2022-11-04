function seeRowsData(){
  var dataRange = sheet.getRange(2, 1, sheet.getLastRow() - 1, sheet.getLastColumn());
  Logger.log(getRowsData(sheet,dataRange));
}

function current_term(l='en'){
  year = today.getFullYear().toString().slice(2,4)
  if (today.getMonth() <=2) {result = (+year-1).toString()+"winter"}
  else if (today.getMonth() == 12) {result = year+"winter"}
  else if (today.getMonth() <=5) {result = year+"spring"}
  else if (today.getMonth() <=8) {result = year+"summer"}
  else {result = year+"fall"}
  if(l=='en'){return result}
  else{
    result = result.replace('winter','冬')
    result = result.replace('spring','春') 
    result = result.replace('summer','夏') 
    result = result.replace('fall','秋')
    return result 
  }
}

function fill_class_data_class(){
  var classes = []
  for (var i = 2; i < sheet.getLastRow(); ++i){
    cl=sheet.getRange(i, 6).getValue()
    if(typeof cl != 'string'){cl=cl.toString()}
    if (!classes.includes(cl)){classes.push(cl)}   
  }
  clss=classes.map(x => [x])
  Logger.log(clss)
  r=classSheet.getRange(2,1,clss.length)
  r.setValues(clss)
}

function fill_class_data_teacher(){
  var teachersClass = teSheet.getRange(1, 5, teSheet.getLastRow()).getValues()
  tc=teachersClass.map(x => x[0].toString())
  Logger.log(tc)
  for (var i = 2; i < classSheet.getLastRow(); ++i){
    cl=classSheet.getRange(i, 1).getValue().toString()
    Logger.log(cl)
    if (tc.includes(cl)){
      indx=tc.indexOf(cl)      
      classSheet.getRange(i, 2).setValue(
        teSheet.getRange(indx+1, 1).getValues()
      )
    }
  }
}

