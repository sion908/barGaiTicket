const descEle = document.getElementById('description');
let sh=descEle.scrollHeight;
let ch=descEle.clientHeight;
liff.init({liffId: this.liff_id,})
    .then(()=>{
        if(!liff.isLoggedIn()){liff.login();}
        const accessToken = liff.getAccessToken();
        // console.log(accessToken);
        const formElements = document.forms.purchaseForm;
        formElements.lineToken.value=accessToken;
})

document.getElementById('next').addEventListener('click',()=>{
    elems=document.getElementsByClassName('radio-inline__input')
    for(var qu of elems){
        if(qu.checked){
            document.getElementById('popup').style.display='block';
            sh=descEle.scrollHeight;
            ch=descEle.clientHeight;
            return
        }
    }
    this.e_tex=document.getElementsByClassName('error_text')[0]
    this.e_tex.hidden=false;
    elems=document.getElementsByClassName('radio-inline__label')
    for(var elem of elems){
        elem.addEventListener('click',
            ()=>this.e_tex.hidden=true);
    }
})
descEle.onscroll=()=>{
    if(sh-(ch+descEle.scrollTop)<1){
        document.getElementsByClassName('pay_btn')[0].disabled=false;
}};