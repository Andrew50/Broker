import{s as k,f as m,a as T,l as g,g as h,h as y,A as $,c as D,m as _,d as v,i as E,x as u,B as S,n as I,y as x}from"../chunks/scheduler.VY-UclLW.js";import{S as j,i as C}from"../chunks/index.QBX9jeLG.js";import{w as P}from"../chunks/index.kYg0fxAy.js";function b(r){let e,t,l='<div><input type="text" name="func" placeholder="func" required=""/></div> <div><input type="text" name="arg1" placeholder="arg1"/></div> <div><input type="text" name="arg2" placeholder="arg2"/></div> <div><input type="text" name="arg3" placeholder="arg3"/></div> <div><input type="text" name="arg4" placeholder="arg4"/></div> <div><input type="text" name="arg5" placeholder="arg5"/></div> <div><input type="text" name="arg6" placeholder="arg6"/></div> <input type="submit" value="FETCH"/>',s,n,i,p,d,f;return{c(){e=m("div"),t=m("form"),t.innerHTML=l,s=T(),n=m("p"),i=g("Result: "),p=g(r[0])},l(o){e=h(o,"DIV",{});var a=y(e);t=h(a,"FORM",{"data-svelte-h":!0}),$(t)!=="svelte-1hoe0xu"&&(t.innerHTML=l),s=D(a),n=h(a,"P",{});var c=y(n);i=_(c,"Result: "),p=_(c,r[0]),c.forEach(v),a.forEach(v)},m(o,a){E(o,e,a),u(e,t),u(e,s),u(e,n),u(n,i),u(n,p),d||(f=S(t,"submit",r[2]),d=!0)},p(o,[a]){a&1&&I(p,o[0])},i:x,o:x,d(o){o&&v(e),d=!1,f()}}}async function q(r,e=!1){event.preventDefault();const t=new FormData(event.target);let l=Array.from(t.values()).join("-"),s;e?s=`${e}-${l}`:s=l;const n=`http://localhost:5057/fetch/${s}`;try{console.log("request sent",n);const i=await fetch(n,{method:"POST",headers:{"Content-Type":"application/json"}});if(!i.ok)throw new Error("POST response not ok");const d=(await i.json()).task_id,o=setInterval(async()=>{const a=await fetch(`http://localhost:5057/poll/${d}`);if(!a.ok)throw new Error("GET response not ok");const c=await a.json(),w=c.status;c.status==="done"?(clearInterval(o),r.set(c.result),console.log(c.result)):w==="failed"&&(clearInterval(o),r.set("failed"))},500)}catch{r.set(null)}}function F(r,e,t){let l=P(),s;return l.subscribe(i=>{t(0,s=i)}),[s,l,i=>q(l)]}class R extends j{constructor(e){super(),C(this,e,F,b,k,{})}}export{R as component};