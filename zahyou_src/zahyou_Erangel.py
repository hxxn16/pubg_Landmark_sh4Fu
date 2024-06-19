import cv2
import numpy as np

# 画像ファイルのパス
image_path = 'static/images/Erangel.JPG'

# 画像を読み込む
image = cv2.imread(image_path)

# テキストを描画する関数
def draw_text_with_outline(img, text, org, font_scale, text_color, outline_color, thickness):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)

    # テキストの描画領域の周囲に線を描く
    outline_thickness = 3
    cv2.putText(img, text, org, font, font_scale, outline_color, thickness + outline_thickness, lineType=cv2.LINE_AA)
    cv2.putText(img, text, org, font, font_scale, text_color, thickness, lineType=cv2.LINE_AA)

# マウスのイベントハンドラ関数
def mouse_event(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        # マウスの位置にあわせて座標を描画する
        image_with_pointer = image.copy()
        coordinates_text = f'({x}, {y})'
        draw_text_with_outline(image_with_pointer, coordinates_text, (x, y), 1.5, (255, 255, 255), (0, 0, 0), 2)  # 太い白文字に変更
        cv2.imshow('Image with Pointer', image_with_pointer)

# ウィンドウを作成して画像を表示する
cv2.namedWindow('Image with Pointer')

# マウスイベントを設定
cv2.setMouseCallback('Image with Pointer', mouse_event)

# 初期画像を表示
cv2.imshow('Image with Pointer', image)

# キー入力を待つ
cv2.waitKey(0)

# ウィンドウを閉じる
cv2.destroyAllWindows()
