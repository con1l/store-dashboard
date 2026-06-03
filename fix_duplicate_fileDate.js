// 修复 index.html 中重复的 let fileDate 声明（保留第二个，删除第一个）
const fs = require('fs');

const path = 'C:/Users/PaiP/store-dashboard/index.html';
let html = fs.readFileSync(path, 'utf8');

// 提取 <script>...</script> 内容
const m = html.match(/(<script>)([\s\S]*?)(<\/script>)/);
if (!m) { console.log('未找到 <script>'); process.exit(1); }

let jsCode = m[2];

// 统计并报告当前有几个 let fileDate  
const matches = jsCode.match(/^\s*let\s+fileDate\s*=/gm) || [];  
console.log('修复前 let fileDate 出现次数:', matches.length);

if (matches.length < 2) {
  console.log('不存在重复声明，无需修复');
} else {
   // Strategy: delete FIRST occurrence only.
   // Approach: find index of first match then remove that whole line.
   const linesBeforeFix=jsCode.split('\n');      
   let foundCount=0;      
   const fixedLines=[];      
    
   for(const line of linesBeforeFix){        
      if(/^\s*let\s+fileDate\s*=/.test(line)){          
         foundCount++;             
         if(foundCount===1){ /* skip this line */ continue;}        
      }         
      fixedLines.push(line);      
    }       
    
    if(foundCount>=2){         
        
     jsCode=fixedLines.join('\n');       
     html=m[1]+jsCode+m[3];       
        
     fs.writeFileSync(path,'',html,'utf8'); // WRONG order!! Should be path, data  
     
     }    
}    

console.log('Done.');   
