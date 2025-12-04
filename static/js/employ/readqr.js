let player, snapshotCanvas, canvasContext, width, height;

window.onload=function(){
  player = document.getElementById('player');
  // console.log(snapshotCanvas);
  snapshotCanvas = document.getElementById('snapshot');
  canvasContext = snapshotCanvas.getContext("2d");
  width = snapshotCanvas.width;
  height = snapshotCanvas.height;


  // このメソッドを呼び出すことでユーザーにブラウザがカメラを使用することを許可するかの確認ダイアログが表示され、
  // 許可されれば handleSuccess が呼ばれる
  navigator.mediaDevices.getUserMedia(
    {
    video: {facingMode: "environment", width: width, height: height},
    audio: false
  }).then(handleSuccess)
  .catch(err => {
    console.log('errro')
    console.log(err);
  });
}

let handleSuccess = (stream) => {//,canvasContext,width,height
  // カメラストリームをプレイヤーのデータに設定
  // console.log(stream)
  player.srcObject = stream;

  startScan((scanResult) => {
    // このページの呼び出し元に読み取り結果を返す
      console.log(scanResult.data);
      mypost(scanResult.data)
      // popupImage;
  });
};

let startScan = (callback) => {
  // 500ms間隔でスナップショットを取得し、QRコードの読み取りを行う
  let intervalHandler = setInterval(() => {
    // console.log(canvasContext);
    canvasContext.drawImage(player, 0, 0, width, height);
    const imageData = canvasContext.getImageData(0, 0, width, height);
    const scanResult = jsQR(imageData.data, imageData.width, imageData.height);

    if (scanResult) {
      clearInterval(intervalHandler);

      if (callback) {
        callback(scanResult);
      }
    }
  }, 500)
};

function mypost(data)
{
    var form = document.forms["send_shop_id"];
    form.elements['shop_id'].value=data;
    form.submit();
}
