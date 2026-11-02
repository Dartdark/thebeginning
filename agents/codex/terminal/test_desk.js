'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {format,selectRows}=require('./static/desk.js');
const set={configurations:{BASE:'BASE',ADD:'ADD',REPLACE:'REPLACE_VB',EMPTY:'EMPTY_VB'}};
test('Missing, non-finite and nonnumeric financial data stay unknown',()=>{
  for(const value of [null,undefined,'',' ','NaN','Infinity','oops',false,{},[]]) assert.equal(format(value,'money'),'Not recorded');
  assert.equal(format('0','money'),'$0');
  assert.equal(format('0.062','percent'),'6.20%');
  assert.equal(format('-2.25','money'),'-$2');
});
test('Account and cohort matching never mixes contexts or picks duplicate rows',()=>{
  const rows=[
    {context:'ES30',account:'150',cohort:'recent',config:'BASE',pass_rate:'0.45'},
    {context:'ES30',account:'50',cohort:'recent',config:'BASE',pass_rate:'0.56'},
    {context:'ES30',account:'150',cohort:'all',config:'BASE',pass_rate:'0.41'},
    {context:'NQ15',account:'150',cohort:'recent',config:'ADD',pass_rate:'0.5'},
    {context:'ES30',account:'150',cohort:'recent',config:'ADD',pass_rate:'0.44'},
    {context:'ES30',account:'150',cohort:'recent',config:'ADD',pass_rate:'0.46'},
    {context:'ES30',account:'150',cohort:'recent',config:'EMPTY_VB',pass_rate:'0.35'}
  ];
  const selected=selectRows(rows,set,'evaluations-150','ES30','recent');
  assert.equal(selected[0].row.pass_rate,'0.45');
  assert.equal(selected[1].row,null);assert.equal(selected[1].issue,'Ambiguous duplicate rows');
  assert.equal(selected[2].row,null);assert.equal(selected[2].issue,'Not recorded');
  assert.equal(selected[3].row.config,'EMPTY_VB');
});
test('Personal has no invented account/cohort filter',()=>{
  const selected=selectRows([{context:'ES30',config:'BASE',annual:'123'}],set,'personal','ES30','recent');
  assert.equal(selected[0].row.annual,'123');assert.equal(selected[1].row,null);
});
