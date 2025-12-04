window.onload=function(){
    const button_com = document.getElementsByClassName('confirm btn');
    const button_back = document.getElementsByClassName('back btn');

    button_com[0].addEventListener('click', trans_to_approve);
    button_back[0].addEventListener('click', return_confirm);

}

function trans_to_approve(){
    const mass = document.select_num.value_num;
  
    // 値(数値)を取得
    const num = mass.selectedIndex;

    // 値(数値)から値(value値)を取得
    const str = mass.options[num].value;
    document.getElementsByClassName('count')[0].textContent=str;
    const Myelement = document.querySelector('input[name="employ_num"]');
    Myelement.value = str;

    document.getElementsByClassName('confirm')[0].style.display='none';
    document.getElementsByClassName('approve')[0].style.display='block';
  
}

function return_confirm(){

    document.getElementsByClassName('confirm')[0].style.display='block';
    document.getElementsByClassName('approve')[0].style.display='none';
  
}
