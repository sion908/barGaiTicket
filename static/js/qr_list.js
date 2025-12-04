// 画像をダウンロードする関数
function downloadImage(dataUrl, filename, zip) {
  // data URLからbase64データを抽出
  var base64Data = dataUrl.split(',')[1];
  zip.file(filename, base64Data, { base64: true });
}

// クラス名を指定して画像をダウンロードする関数
function downloadImagesByClass() {
  const className = "qr_img";
  var elements = document.getElementsByClassName(className);
  var zip = new JSZip();

  for (var i = 0; i < elements.length; i++) {
      var imgElement = elements[i];
      var dataUrl = imgElement.src;

      // ダウンロードする画像のファイル名を指定（例: image1.png）
      var filename = imgElement.name.replace(/[ 　]/g,'_') + '_img.png';

      downloadImage(dataUrl, filename, zip);
  }

  // ZIPファイルを生成してダウンロード
  zip.generateAsync({ type: 'blob' }).then(function (content) {
      // ダウンロードするZIPファイルのファイル名を指定
      var zipFilename = 'images.zip';
      saveAs(content, zipFilename);
  });
}

const qr_list_elem = document.getElementById("qr_list");
const a_elem = document.createElement("a");
const button_elem = document.createElement("button");
button_elem.type="button";
button_elem.addEventListener('click', downloadImagesByClass);
button_elem.textContent="QRの画像をダウンロードする";
qr_list_elem.prepend(button_elem);
