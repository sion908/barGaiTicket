window.onload = function(){
    document.querySelector(".rotate").animate(
        [{ transform: 'rotate(0deg)' },
            { transform: 'rotate(180deg)' }
        ],
        {
            duration: 1000,
            easing: 'ease',
            // iterations: Infinity
            fill:"forwards",
            done:rotdone()
        }
    );
}

function rotdone(){
    setTimeout(()=>document.querySelector('.tohome').style.display = "block",2000)
}