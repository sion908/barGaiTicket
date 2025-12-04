var video = document.createElement("video");
var canvasElement = document.getElementById("canvas");
var canvas = canvasElement.getContext("2d");
var loadingMessage = document.getElementById("loadingMessage");
var reg=/https:\/\/liff.line.me\/1657251421-rW78w9bW\/employ\/\?ver=2023-f&shop_id=([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/;
var batsudiv=document.getElementsByClassName('batsu')[0];
this.a1=document.getElementsByClassName('1a');
this.s1=document.getElementsByClassName('1s');
this.a2=document.getElementsByClassName('2a');
this.s2=document.getElementsByClassName('2s');


function drawLine(begin, end, color) {
    canvas.beginPath();
    canvas.moveTo(begin.x, begin.y);
    canvas.lineTo(end.x, end.y);
    canvas.lineWidth = 4;
    canvas.strokeStyle = color;
    canvas.stroke();
}

// Use facingMode: environment to attemt to get the front camera on phones
const startScan=()=>navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function(stream) {
    video.srcObject = stream;
    video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
    video.play();
    requestAnimationFrame(tick);
});

function tick() {
    loadingMessage.innerText = "⌛ Loading video..."
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
    loadingMessage.hidden = true;
    canvasElement.hidden = false;
    ccw=document.getElementsByClassName('container')[0].clientWidth

    canvasElement.height = ccw;
    canvasElement.width = ccw;
    let h=video.videoHeight, w=video.videoWidth;
    if(h<w){
        canvas.drawImage(video, Math.floor((w-ccw)/2), 0, ccw, ccw);
    }else{
        canvas.drawImage(video,0,Math.floor((h-ccw)/2),ccw, ccw);
    }
    var imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
    var code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: "dontInvert",
    });
    if (code) {
        drawLine(code.location.topLeftCorner, code.location.topRightCorner, "#FF3B58");
        drawLine(code.location.topRightCorner, code.location.bottomRightCorner, "#FF3B58");
        drawLine(code.location.bottomRightCorner, code.location.bottomLeftCorner, "#FF3B58");
        drawLine(code.location.bottomLeftCorner, code.location.topLeftCorner, "#FF3B58");
        var res = code.data.match(reg);
        if(res){
            confQR(res[1])
            return
        }
    }
    }
    requestAnimationFrame(tick);
    
}

function inputDescriptions(shop){
    const elem = document.getElementsByClassName('shopName')[0];
    var text =`店名:${shop.name}`;
    elem.innerHTML = text;
    document.getElementById('popup').style.display='block';
}

const confQR=(uuid)=>{
    fetch(`/api/shop/${this.accessToken}/${uuid}`, {redirect: 'follow'})
        .then((res)=>res.json())
        .then(data => {
            if("url" in data){
                window.location.href=data.url;
            }
            this.data = data
            inputDescriptions(data.shop);
            if(this.data.user.maxuse){
                document.forms.employForm.shop_id.value=uuid
                selectElem=document.getElementById("select_num")
                for(var i=1;i<=data.user.maxuse;i++){
                    const option1 = document.createElement('option');
                    option1.value = String(i);
                    option1.textContent = String(i);
                    selectElem.appendChild(option1)
                }
                _elem=document.getElementById("appear_price_c")
                _elem.innerText=selectElem.value*500
            }else{
                if(!this.data.user.used){
                    window.location.href='/line/trans/purchase'
                }
                document.getElementById('btn-next').hidden=true;
                document.getElementsByClassName('select_num_cover')[0].hidden=true;
                document.getElementsByClassName('non_ticket')[0].hidden=false;
            }
            return
        })
        .catch(e=>{
            tick()
        });
}

const form = document.forms.employForm
const submitButton = document.forms.employForm.submitBtn

const submitEmployForm = () => {
  batsudiv.disabled=true
  const formData = new FormData(form)
  const action = form.getAttribute("action")
  const options = {
    method: 'POST',
    body: formData,
  }
  fetch(action, options).then((e) => {
    if(e.status === 200) {
      document.getElementById('loading').innerText=''
      document.getElementById('description').animate(
      { transform: 'rotate(0deg)' },
      {
          duration: 500,
          easing: 'linear',
          iterations: 1,
          fill:'forwards'
      });
      for(const ele of this.a2){ele.hidden=false;}
      for(const ele of this.s2){ele.hidden=true;}
    }
    // alert("保存できませんでした。")
  });
  form.hidden=true;
  mkload();
}

batsudiv.onclick=()=>{
  document.getElementById('popup').style.display='none';
  selectElem = document.getElementById('select_num');
  var clone = selectElem.cloneNode( false ); //ガワだけ複製して…
  selectElem.parentNode.replaceChild( clone , selectElem ); //すげ替え。
  startScan()
}

const check_conf=(value)=>{document.forms.employForm.submitBtn.disabled=!value}

this.orig={}
const moverElem=document.getElementById("mover");
const slide_out=document.getElementsByClassName('btn-slide-out')[0]
let slideSize=parseInt(slide_out.clientWidth-moverElem.clientWidth);
const reach=()=>{
    moverElem.style.marginLeft=slideSize+"px";
    moverElem.removeEventListener('touchend', eT,{passive:true});
    moverElem.addEventListener('touchend', submitEmployForm,{passive:true});
}
const sT=(e)=>{this.origX=e.touches[0].pageX;slideSize=parseInt(slide_out.clientWidth-moverElem.clientWidth);}
const eT=(e)=>moverElem.style.marginLeft=0;
const mT=(e)=>{
    slideSize=parseInt(slide_out.clientWidth-moverElem.clientWidth);
    const div=e.touches[0].pageX-this.origX;
    if(div>slideSize){reach();return}else if(div<0){eT();return}
    moverElem.addEventListener('touchend', eT,{passive:true});
    moverElem.removeEventListener('touchend', submitEmployForm,{passive:true});
    moverElem.style.marginLeft=div+"px";
    // console.log("m",e.touches[0].pageX,e.touches[0].pageX-this.origX)
};
moverElem.addEventListener('touchstart', sT,{passive:true});
moverElem.addEventListener('touchmove', mT,{passive:true});
moverElem.addEventListener('touchend', eT,{passive:true});
moverElem.addEventListener('touchcansel', eT,{passive:true});

document.getElementById("btn-next").addEventListener('click',()=>{
    const used_num = document.getElementById('select_num').value;
    if(used_num=="0"){return}
    const option1 = document.getElementById('appear_num');
    option1.innerHTML = used_num;
    _elem=document.getElementById("appear_price_s");
    _elem.innerText=used_num*500;

    const descElem = document.getElementById('description');
    descElem.animate(
        { transform: 'rotate(180deg)' },
        {
            duration: 500,
            easing: 'linear',
            iterations: 1,
            fill:'forwards'
        }
    );
    for(const ele of this.a1){ele.hidden=false;}
    for(const ele of this.s1){ele.hidden=true;}
})

document.getElementById('btn-back').onclick=()=>{
    document.getElementById('description').animate(
            { transform: 'rotate(0deg)' },
            {
                duration: 500,
                easing: 'linear',
                iterations: 1,
                fill:'forwards'
    });
    for(const ele of this.a1){ele.hidden=true;}
    for(const ele of this.s1){ele.hidden=false;}
}
document.getElementById('select_num').addEventListener(`change`, () => {
    _elem=document.getElementById("appear_price_c")
    _elem.innerText=selectElem.value*500
});