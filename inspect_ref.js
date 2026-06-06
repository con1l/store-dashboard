var XLSX=require('xlsx');
var wb=XLSX.readFile('D:\\Edge download\\已整理\\25年\\25年3、4、5月门店.xlsx',{cellDates:true});
var ws=wb.Sheets['支付明细'];
// 找日均在第几列
var range=XLSX.utils.decode_range(ws['!ref']);
console.log('Total cols:',range.e.c+1,'Total rows:',range.e.r+1);
// 打印第1行所有列名
console.log('\n--- 第1行列名 ---');
for(var c=0;c<=range.e.c;c++){
  var cell=XLSX.utils.encode_cell({r:0,c:c});
  var val=ws[cell]?ws[cell].v:'(空)';
  console.log(XLSX.utils.encode_col(c),':',val);
}
// 打印第2行前几列数据
console.log('\n--- 第2行数据 ---');
for(var c=0;c<=Math.min(range.e.c,20);c++){
  var cell=XLSX.utils.encode_cell({r:1,c:c});
  var val=ws[cell]?ws[cell].v:'(空)';
  console.log(XLSX.utils.encode_col(c),':',val);
}
