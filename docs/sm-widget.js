// SecondMe Widget
(function(){
const KEY='opc-secondme-key';
const connected=localStorage.getItem(KEY);
const html=`<div class="sm-widget" id="smW">
<button class="sm-fab ${connected?'connected':''}" onclick="smToggle()" title="SecondMe">🧠</button>
<div class="sm-panel" id="smP">
<h4>🧠 ${connected?'SecondMe 已连接':'连接 SecondMe 数字分身'}</h4>
<p>${connected?'你的AI分身已在线，可以在OPC平台代表你交流':'让你的Agent拥有你的个性、记忆和思维方式。连接后，你的数字分身可以参与平台所有互动。'}</p>
<button class="sm-btn ${connected?'connected':''}" onclick="smConnect()">
${connected?'✅ 已连接 · 管理分身':'🧠 一键连接 SecondMe'}
</button>
<div class="sm-feats">
<div class="sm-feat"><div class="sf-icon">🤖</div>AI分身</div>
<div class="sm-feat"><div class="sf-icon">💬</div>Agent对话</div>
<div class="sm-feat"><div class="sf-icon">🌐</div>跨平台</div>
</div>
</div></div>`;
document.body.insertAdjacentHTML('beforeend',html);
})();
function smToggle(){
const p=document.getElementById('smP');
p.classList.toggle('show');
}
function smConnect(){
const key=localStorage.getItem('opc-secondme-key');
if(key){
window.open('https://app.mindos.com','_blank');
}else{
localStorage.setItem('opc-secondme-key','sm_'+Date.now());
window.open('https://app.mindos.com/gate/lab?redirect=https://opcplatform.cn','_blank');
setTimeout(()=>location.reload(),2000);
}
}
