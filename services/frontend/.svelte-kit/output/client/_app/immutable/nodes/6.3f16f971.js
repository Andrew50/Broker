import{S as Z,i as ee,s as te,k as r,a as y,q as W,l as s,m as d,h as u,c as _,r as X,n as a,b as ae,G as e,J as re,u as se,H as Y}from"../chunks/index.575d8db5.js";import{w as ne}from"../chunks/index.9a5a6444.js";function le(h){let l,t,i,o,I,p,g,V,E,v,T,c,f,j,N,P,q,U,w,C,$,k,F,S,O,x,R,b,G,A;return{c(){l=r("div"),t=r("form"),i=r("div"),o=r("input"),I=y(),p=r("div"),g=r("input"),V=y(),E=r("div"),v=r("input"),T=y(),c=r("div"),f=r("input"),j=y(),N=r("div"),P=r("input"),q=y(),U=r("div"),w=r("input"),C=y(),$=r("div"),k=r("input"),F=y(),S=r("input"),O=y(),x=r("p"),R=W("Result: "),b=W(h[0]),this.h()},l(D){l=s(D,"DIV",{});var m=d(l);t=s(m,"FORM",{});var n=d(t);i=s(n,"DIV",{});var J=d(i);o=s(J,"INPUT",{type:!0,name:!0,placeholder:!0}),J.forEach(u),I=_(n),p=s(n,"DIV",{});var M=d(p);g=s(M,"INPUT",{type:!0,name:!0,placeholder:!0}),M.forEach(u),V=_(n),E=s(n,"DIV",{});var z=d(E);v=s(z,"INPUT",{type:!0,name:!0,placeholder:!0}),z.forEach(u),T=_(n),c=s(n,"DIV",{});var B=d(c);f=s(B,"INPUT",{type:!0,name:!0,placeholder:!0}),B.forEach(u),j=_(n),N=s(n,"DIV",{});var K=d(N);P=s(K,"INPUT",{type:!0,name:!0,placeholder:!0}),K.forEach(u),q=_(n),U=s(n,"DIV",{});var L=d(U);w=s(L,"INPUT",{type:!0,name:!0,placeholder:!0}),L.forEach(u),C=_(n),$=s(n,"DIV",{});var Q=d($);k=s(Q,"INPUT",{type:!0,name:!0,placeholder:!0}),Q.forEach(u),F=_(n),S=s(n,"INPUT",{type:!0}),n.forEach(u),O=_(m),x=s(m,"P",{});var H=d(x);R=X(H,"Result: "),b=X(H,h[0]),H.forEach(u),m.forEach(u),this.h()},h(){a(o,"type","text"),a(o,"name","func"),a(o,"placeholder","func"),o.required=!0,a(g,"type","text"),a(g,"name","arg1"),a(g,"placeholder","arg1"),a(v,"type","text"),a(v,"name","arg2"),a(v,"placeholder","arg2"),a(f,"type","text"),a(f,"name","arg3"),a(f,"placeholder","arg3"),a(P,"type","text"),a(P,"name","arg4"),a(P,"placeholder","arg4"),a(w,"type","text"),a(w,"name","arg5"),a(w,"placeholder","arg5"),a(k,"type","text"),a(k,"name","arg6"),a(k,"placeholder","arg6"),a(S,"type","submit"),S.value="FETCH"},m(D,m){ae(D,l,m),e(l,t),e(t,i),e(i,o),e(t,I),e(t,p),e(p,g),e(t,V),e(t,E),e(E,v),e(t,T),e(t,c),e(c,f),e(t,j),e(t,N),e(N,P),e(t,q),e(t,U),e(U,w),e(t,C),e(t,$),e($,k),e(t,F),e(t,S),e(l,O),e(l,x),e(x,R),e(x,b),G||(A=re(t,"submit",h[2]),G=!0)},p(D,[m]){m&1&&se(b,D[0])},i:Y,o:Y,d(D){D&&u(l),G=!1,A()}}}async function oe(h,l=!1){event.preventDefault();const t=new FormData(event.target);let i=Array.from(t.values()).join("-"),o;l?o=`${l}-${i}`:o=i;const I=`http://localhost:5057/fetch/${o}`;try{console.log("request sent",I);const p=await fetch(I,{method:"POST",headers:{"Content-Type":"application/json"}});if(!p.ok)throw new Error("POST response not ok");const V=(await p.json()).task_id,v=setInterval(async()=>{const T=await fetch(`http://localhost:5057/poll/${V}`);if(!T.ok)throw new Error("GET response not ok");const c=await T.json(),f=c.status;c.status==="done"?(clearInterval(v),h.set(c.result),console.log(c.result)):f==="failed"&&(clearInterval(v),h.set("failed"))},500)}catch{h.set(null)}}function ie(h,l,t){let i=ne(),o;return i.subscribe(p=>{t(0,o=p)}),[o,i,p=>oe(i)]}class ce extends Z{constructor(l){super(),ee(this,l,ie,le,te,{})}}export{ce as component};
