var XLSX=require('xlsx');
var wb=XLSX.readFile('D:\\Edge download\\已整理\\25年\\25年3、4、5月门店.xlsx',{cellDates:true});
var ws=wb.Sheets['支付明细'];
// show data rows (A2-B5)
console.log('=== 数据行 ===');
for(var r=2;r<=8;r++){
  var row=[];
  for(var c='A';c<='E';c++){
    var cell=ws[c+r];
    row.push(cell!=null?cell.v:'');
  }
  console.log(r+':',row.join(' | '));
}
// show a trend sheet
console.log('\n=== 茌平趋势数据 ===');
var ws2=wb.Sheets['茌平趋势数据'];
var keys2=Object.keys(ws2).filter(function(k){return k[0]!=='!'}).slice(0,20);
keys2.forEach(function(k){console.log(k,':',JSON.stringify(ws2[k]))});
if(ws2['!merges'])ws2['!merges'].forEach(function(m){console.log('merge:',JSON.stringify(m))});
