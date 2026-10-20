// Test-only stand-in for supabase-js: an in-memory database shared between browser tabs. Not used by the app.
(function(){
  const bc=new BroadcastChannel('fake-sb');
  const K='fake_db';
  const load=()=>JSON.parse(localStorage.getItem(K)||'{"seq":0,"rows":[]}');
  const save=d=>localStorage.setItem(K,JSON.stringify(d));
  const listeners=new Set(), presence=new Map(); // key -> {tab}
  const tab=Math.random().toString(36).slice(2);
  bc.onmessage=e=>{const m=e.data;
    if(m.t==='insert')listeners.forEach(l=>l.pg&&l.pg({new:m.row}));
    if(m.t==='bcast')listeners.forEach(l=>l.bc&&l.name===m.name&&l.bc(m.event,{payload:m.payload}));
    if(m.t==='pres'){m.on?presence.set(m.key,m.tab):presence.delete(m.key);listeners.forEach(l=>l.ps&&l.ps());}
    if(m.t==='hello'){presenceMine.forEach(k=>bc.postMessage({t:'pres',on:true,key:k,tab}));}
  };
  const presenceMine=new Set();
  function Q(table){
    const q={f:[],op:'select',order:null,lim:null,payload:null,single:false,sel:false};
    const b={
      select(){q.sel=true;return b},insert(p){q.op='insert';q.payload=p;return b},delete(){q.op='delete';return b},
      eq(c,v){q.f.push(r=>String(r[c])===String(v));return b},in(c,a){q.f.push(r=>a.includes(r[c]));return b},
      lt(c,v){q.f.push(r=>c==='created_at'?Date.parse(r[c])<Date.parse(v):r[c]<v);return b},
      gt(c,v){q.f.push(r=>Date.parse(r[c])>Date.parse(v));return b},
      order(c,o){q.order=[c,o&&o.ascending!==false];return b},limit(n){q.lim=n;return b},single(){q.single=true;return b},
      then(res,rej){return run().then(res,rej)}
    };
    async function run(){
      const d=load();
      if(q.op==='insert'){const row={id:++d.seq,created_at:new Date().toISOString(),...q.payload};d.rows.push(row);save(d);
        listeners.forEach(l=>l.pg&&l.pg({new:row}));bc.postMessage({t:'insert',row});
        return{data:q.single?{id:row.id,created_at:row.created_at}:[row],error:null}}
      let rows=d.rows.filter(r=>q.f.every(f=>f(r)));
      if(q.op==='delete'){d.rows=d.rows.filter(r=>!rows.includes(r));save(d);return{data:null,error:null}}
      if(q.order){const[c,asc]=q.order;rows.sort((a,b)=>{const x=c==='created_at'?Date.parse(a[c]):a[c],y=c==='created_at'?Date.parse(b[c]):b[c];return asc?x-y:y-x||(asc?a.id-b.id:b.id-a.id)})}
      if(q.lim)rows=rows.slice(0,q.lim);
      return{data:q.single?rows[0]:rows,error:null};
    }
    return b;
  }
  window.supabase={createClient(){return{
    from:Q,
    channel(name,opts){
      const l={name,pg:null,bc:null,ps:null};const ch={
        on(type,filter,cb){ if(type==='postgres_changes')l.pg=cb; else if(type==='broadcast')l.bc=(ev,p)=>filter.event===ev&&cb(p); else if(type==='presence')l.ps=cb; return ch},
        subscribe(cb){listeners.add(l);setTimeout(()=>cb&&cb('SUBSCRIBED'),30);return ch},
        send(m){bc.postMessage({t:'bcast',name,event:m.event,payload:m.payload});return Promise.resolve()},
        async track(){const key=opts&&opts.config&&opts.config.presence&&opts.config.presence.key;presenceMine.add(key);presence.set(key,tab);bc.postMessage({t:'pres',on:true,key,tab});bc.postMessage({t:'hello'});l.ps&&l.ps()},
        presenceState(){const o={};presence.forEach((v,k)=>o[k]=[{}]);return o},
        _l:l};
      return ch},
    removeChannel(ch){listeners.delete(ch._l);return Promise.resolve()}
  }}};
})();
