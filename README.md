# バル街チケット関連システム

## やろうと思うこと

[] 多言語対応をあきらめた分，モデル等を翻訳

## そのうちやりたいこと

[] 多言語対応 -> やるならAWSに持っていく必要がありそう



## デバッグについて

```python
import pdb
pdb.set_trace() 
```
`docker attach web`でコンテナ内に入ればwebの時も行ける

これを適当につっこむ

## パッケージ依存関係について

`$ pip freeze -> requirements.txt`
これで一発
```
Django==4.0.3
...
```
こんな感じ

## 画像の保存回り

cloudinaryを利用
これで利用可能
`<img src="{{ test_model_instance.image.url }}" alt="{{ test_model_instance.image.name }}">`

https://cloudinary.com/console/c-f4e0b9a75d433d9d77fa9022ed5cc4
参考 : https://qiita.com/koki276/items/4f78ca421bea059d7b7a

## 支払い関係

stripe VS payjs

payjsは日本製
ちょっと安い

とりあえずstripeでやってきたのでそっちで
リッチにするときに考える


https://liff.line.me/1657454732-a5NPKAql/employ/?ver=2023-f&shop_id=33cf177e-6e30-4c22-92c2-4aea1d4aaf57
https://liff.line.me/1657454732-a5NPKAql/employ/?ver=2023-f&shop_id=33cf177e-6e30-4c22-92c2-4aea1d4aaf57