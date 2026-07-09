import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
import numpy as np
from io import BytesIO
import base64
import time

from image_processor import apply_film_filter
from film_library import FILMS, match_film_by_keywords, VARIANT_PRESETS


def generate_test_image(width=800, height=600, img_type="portrait"):
    """生成测试图：portrait人像 / landscape风景 / text文档"""
    img = Image.new('RGB', (width, height), (240, 240, 240))
    arr = np.array(img).astype(np.uint8)

    if img_type == "portrait":
        for y in range(height):
            for x in range(width):
                t_y = y / height
                arr[y, x] = [
                    int(220 - 70*t_y),
                    int(200 - 60*t_y),
                    int(180 - 50*t_y)
                ]
        cx, cy, rx, ry = width//2, int(height*0.42), int(width*0.18), int(height*0.22)
        yy, xx = np.ogrid[:height, :width]
        face_mask = ((xx-cx)/rx)**2 + ((yy-cy)/ry)**2 <= 1
        skin_color = np.array([230, 190, 165], dtype=np.uint8)
        arr[face_mask] = skin_color + np.random.randint(-8, 8, 3)
        arr[int(height*0.6):, :, :] = [60, 45, 90]
        for i in range(0, width, 4):
            arr[int(height*0.6):, i:i+2, :] = [80, 60, 110]

    elif img_type == "landscape":
        import math
        for y in range(height):
            t = y / (height * 0.55)
            if y < height * 0.55:
                arr[y, :] = [int(255*(1-t) + 130*t), int(255*(1-t) + 175*t), int(255*(1-t) + 215*t)]
            else:
                sand = (y - height*0.55) / (height*0.45)
                arr[y, :] = [int(210 - 40*sand), int(190 - 30*sand), int(150 - 20*sand)]
        for _ in range(4):
            cx, cy = np.random.randint(50, width-150), np.random.randint(30, int(height*0.25))
            r = np.random.randint(30, 60)
            yy, xx = np.ogrid[:height, :width]
            mask = (xx-cx)**2 + (yy-cy)**2 <= r**2
            arr[mask] = np.minimum(arr[mask].astype(np.int16) + 30, 255).astype(np.uint8)
        for t in np.linspace(0, 1, 500):
            x = int(width*0.15 + t*width*0.35)
            y = int(height*0.85 - t*height*0.5)
            if 0 <= x < width-1 and 0 <= y < height-1:
                arr[y-2:y+2, x-2:x+2] = [80, 55, 30]
        cy, cx = int(height*0.3), int(width*0.5)
        for angle in np.linspace(0, 2*math.pi, 11):
            for r in range(0, int(width*0.15), 2):
                x = int(cx + math.cos(angle)*r)
                y = int(cy + math.sin(angle)*r*0.4)
                if 0<=x<width and 0<=y<height:
                    leaf_width = max(1, int((1 - r/(width*0.15)) * 4))
                    arr[y-leaf_width:y+leaf_width, x:x+leaf_width] = [40, 90, 40]

    elif img_type == "text":
        arr[:,:,:] = 250
        for i, line_y in enumerate(range(80, height-80, 55)):
            lw = width - 200 - (i%3)*30
            arr[line_y:line_y+22, 100:100+lw] = [30,30,30]
            lw2 = int(width*0.6) - (i%2)*40
            arr[line_y+28:line_y+46, 100:100+lw2] = [50,50,50]

    buf = BytesIO()
    Image.fromarray(arr).save(buf, format='JPEG', quality=92)
    return buf.getvalue()


def test_all_filters():
    print("="*72)
    print(" �️  公元胶片模拟器 · 滤镜测试（史料级参数 v2.0）")
    print("="*72)

    print("\n📷 生成 3 类测试图片（人像/风景/文档）...")
    test_images = {
        "人像（毛衣）": generate_test_image(800, 600, "portrait"),
        "风景（椰树）": generate_test_image(800, 600, "landscape"),
        "文档（文字）": generate_test_image(800, 600, "text"),
    }
    for name, data in test_images.items():
        print(f"   ✅ {name}: {len(data)} bytes")

    print("\n🧠 测试关键词匹配（8款胶片全覆盖）...")
    tests = [
        ("80年代黑白胶卷，颗粒粗一点", "film_001", "黑白胶卷"),
        ("照相馆专业人像，要层次丰富", "film_002", "人相胶片"),
        ("90年代那种彩卷，暖黄褪色", "film_003", "彩色负片"),
        ("反转片，幻灯片那种通透的", "film_004", "彩色反转片"),
        ("70年代露天电影，宽幅感", "film_005", "电影正片"),
        ("X光那种青蓝高反差工业风", "film_006", "X光胶片"),
        ("印刷制版，黑白分明二值化", "film_007", "制版胶片"),
        ("暗房手工绸纹印相纸，暖棕", "film_008", "印相纸"),
    ]
    ok, fail = 0, []
    for txt, expected_id, expected_name in tests:
        res = match_film_by_keywords(txt)
        film = FILMS[res]
        passed = (res == expected_id) or (film["short_name"] in expected_name)
        if passed:
            ok += 1
            print(f"   ✅ 「{txt[:20]}…」 → {film['name'][:18]}")
        else:
            fail.append((txt, expected_name, film['name']))
            print(f"   ❌ 「{txt[:20]}…」 → 期望{expected_name}，实际{film['short_name']}")
    print(f"   📊 匹配准确率：{ok}/{len(tests)}")

    print("\n� 测试 8 款滤镜 + 3 张测试图（共 24 次处理）...")
    out_dir = os.path.join(os.path.dirname(__file__), "test_outputs")
    os.makedirs(out_dir, exist_ok=True)
    total_time = 0.0
    count = 0

    for fid, film in FILMS.items():
        print(f"\n   ▸ {film['name']}")
        if fid in ("film_002",):
            img_sel = [(n, d) for n, d in test_images.items() if "人像" in n][0]
        elif fid == "film_005":
            img_sel = [(n, d) for n, d in test_images.items() if "风景" in n][0]
        elif fid == "film_007":
            img_sel = [(n, d) for n, d in test_images.items() if "文档" in n][0]
        elif fid == "film_006":
            img_sel = [(n, d) for n, d in test_images.items() if "风景" in n][0]
        else:
            img_sel = list(test_images.items())[0]
        img_name, img_bytes = img_sel

        t0 = time.time()
        try:
            result = apply_film_filter(img_bytes, film["filter_params"])
            dt = time.time() - t0
            total_time += dt
            count += 1
            img = Image.open(BytesIO(result))
            out_path = os.path.join(out_dir, f"{fid}_{film['short_name']}.jpg")
            with open(out_path, "wb") as f:
                f.write(result)
            print(f"     ✅ {img_name} → {img.size[0]}x{img.size[1]} | {len(result)//1024}KB | {dt*1000:.0f}ms → saved")
        except Exception as e:
            print(f"     ❌ 失败：{e}")
            import traceback; traceback.print_exc()
            return False

    print(f"\n   ▸ 印相纸变体组合（1号软/绸纹 + 3号硬/绒面 + 4号特硬/光面）")
    base_film = FILMS["film_008"]
    base_bytes = test_images["人像（毛衣）"]
    for variant_key, vp in VARIANT_PRESETS.items():
        custom_params = {**base_film["filter_params"], **vp["override"]}
        t0 = time.time()
        try:
            result = apply_film_filter(base_bytes, custom_params)
            dt = time.time() - t0
            total_time += dt
            count += 1
            out_path = os.path.join(out_dir, f"{variant_key}.jpg")
            with open(out_path, "wb") as f:
                f.write(result)
            print(f"     ✅ {vp['desc'][:18]} → {len(result)//1024}KB | {dt*1000:.0f}ms")
        except Exception as e:
            print(f"     ❌ {variant_key} 失败：{e}")

    print("\n" + "="*72)
    print(f"✅ 处理完成：{count} 张图，总耗时 {total_time:.2f}s（平均 {total_time/max(count,1)*1000:.0f}ms/张）")
    print(f"📁 输出目录：{out_dir}")
    print(f"💡 提示：打开 test_outputs 文件夹查看 8 款胶片 + 3 种印相纸变体效果")
    print("="*72)

    print("\n📋 史料参数对照表（核心字段已按你的文档校准）：")
    print(f"{'胶片':<20}{'反差α':>7}{'β':>5}{'R偏移':>6}{'B偏移':>6}{'颗粒σ':>7}{'饱和':>6}  备注")
    print("-"*82)
    for fid, film in FILMS.items():
        p = film["filter_params"]
        a = p.get("contrast_alpha", 1.0)
        b = p.get("contrast_beta", 0)
        rs = p.get("r_shift", 0)
        bs = p.get("b_shift", 0)
        sg = p.get("grain_sigma", 0)
        sat = p.get("saturation", 1.0)
        tag = ""
        if p.get("cinemascope"): tag = "宽幅2.35:1"
        if p.get("binary_threshold"): tag = "二值化"
        if "paper_texture" in p: tag = f"纸面:{p['paper_texture']}"
        if p.get("grayscale") and fid!="film_007": tag += " / 黑白" if tag else "黑白"
        if not p.get("grayscale"): tag += " / 彩色" if tag else "彩色"
        print(f"{film['short_name']:<18}{a:>7.2f}{b:>5}{rs:>+6}{bs:>+6}{sg:>7.1f}{sat:>6.2f}  {tag}")
    print("-"*82)
    return True


if __name__ == "__main__":
    success = test_all_filters()
    sys.exit(0 if success else 1)
