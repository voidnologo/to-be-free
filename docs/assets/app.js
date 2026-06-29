
(function(){
  var R = window.SITE_ROOT || "./";
  // mobile sidebar
  var side=document.getElementById('side'), scrim=document.getElementById('scrim'),
      hamb=document.getElementById('hamb');
  function close(){side&&side.classList.remove('open');scrim&&scrim.classList.remove('on');}
  hamb&&hamb.addEventListener('click',function(){var o=side.classList.toggle('open');
    scrim.classList.toggle('on',o);});
  scrim&&scrim.addEventListener('click',close);
  // ensure current sidebar item visible
  var cur=document.querySelector('.side-sec[open] li a[href$="'+location.pathname.split('/').pop()+'"]');

  // live search
  var q=document.getElementById('q'), box=document.getElementById('results'), idx=null;
  function load(cb){ if(idx){cb();return;}
    fetch(R+'search-index.json').then(function(r){return r.json();}).then(function(d){idx=d;cb();}); }
  function esc(s){return (s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function run(){
    var v=q.value.trim().toLowerCase();
    if(!v){box.classList.remove('on');box.innerHTML='';return;}
    load(function(){
      var terms=v.split(/\s+/), out=[];
      for(var i=0;i<idx.length && out.length<14;i++){
        var d=idx[i], hay=(d.t+' '+d.a+' '+d.s+' '+(d.g||[]).join(' ')).toLowerCase();
        if(terms.every(function(t){return hay.indexOf(t)>-1;})) out.push(d);
      }
      if(!out.length){box.innerHTML='<div class="none">No documents match.</div>';box.classList.add('on');return;}
      box.innerHTML=out.map(function(d){return '<a href="'+R+d.u+'"><span class="r-s">'+esc(d.s)+
        '</span><br>'+esc(d.t)+'<br><span class="r-a">'+esc(d.a)+'</span></a>';}).join('');
      box.classList.add('on');
    });
  }
  if(q){
    q.addEventListener('input',run);
    q.addEventListener('focus',run);
    document.addEventListener('click',function(e){ if(!e.target.closest('.search')) box.classList.remove('on'); });
    document.addEventListener('keydown',function(e){ if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus();}
      if(e.key==='Escape')box.classList.remove('on'); });
  }

  // browse filter (+ ?q= prefill from tag links / global search)
  var filter=document.getElementById('filter');
  if(filter){
    var params=new URLSearchParams(location.search), pre=params.get('q');
    function apply(){
      var v=(filter.value||'').trim().toLowerCase(), any=false;
      document.querySelectorAll('.blist li').forEach(function(li){
        var hit=!v||li.getAttribute('data-text').indexOf(v)>-1;
        li.style.display=hit?'':'none'; if(hit)any=true;
      });
      document.querySelectorAll('.bsec').forEach(function(s){
        var vis=s.querySelector('.blist li:not([style*="none"])');
        s.style.display=vis?'':'none';
      });
      document.querySelectorAll('.grp').forEach(function(g){
        var n=g.nextElementSibling, show=false;
        while(n&&!n.classList.contains('grp')){ if(n.classList.contains('bsec')&&n.style.display!=='none')show=true; n=n.nextElementSibling;}
        g.style.display=show?'':'none';
      });
      var fe=document.getElementById('fempty'); if(fe)fe.hidden=any;
    }
    filter.addEventListener('input',apply);
    if(pre){filter.value=pre;apply();}
  }
})();
