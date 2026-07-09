import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import base64
import os
from typing import Dict, Any, Tuple, Optional


def _channel_shift_bgr(img_bgr: np.ndarray, r_delta: int = 0, g_delta: int = 0, b_delta: int = 0) -> np.ndarray:
    """直接按通道加减色偏（依据史料：R+15, B-8 等）"""
    result = img_bgr.copy().astype(np.int16)
    if r_delta: result[:, :, 2] += r_delta
    if g_delta: result[:, :, 1] += g_delta
    if b_delta: result[:, :, 0] += b_delta
    return np.clip(result, 0, 255).astype(np.uint8)


def _contrast_alpha_beta(img_bgr: np.ndarray, alpha: float = 1.0, beta: int = 0) -> np.ndarray:
    """史料级 alpha/beta 对比度公式：g(i,j) = α·f(i,j) + β"""
    result = img_bgr.astype(np.float32) * alpha + float(beta)
    return np.clip(result, 0, 255).astype(np.uint8)


def _silver_grain(img_bgr: np.ndarray, sigma: float = 12.0, content_aware: bool = True) -> np.ndarray:
    """银盐颗粒：高斯噪声 × 局部方差权重图（模拟真实相纸颗粒不均匀分布）"""
    if sigma <= 0:
        return img_bgr
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # 生成基础噪声
    noise = np.random.normal(0, sigma, (h, w)).astype(np.float32)

    if content_aware:
        # 计算局部方差（暗部+平坦区域颗粒更明显，高亮/纹理区颗粒轻）
        blur = cv2.GaussianBlur(gray, (21, 21), 3.5)
        local_var = cv2.GaussianBlur((gray - blur) ** 2, (21, 21), 3.5)
        # 归一化权重：平坦暗部 → 权重高，纹理亮部 → 权重低
        weight = 1.0 - np.clip(local_var / (local_var.max() + 1e-6), 0, 1)
        darkness = 1.0 - (gray / 255.0)
        weight = weight * (0.35 + 0.65 * darkness)
        noise = noise * weight

    # 三通道叠加（彩照偏色颗粒）
    if len(img_bgr.shape) == 3:
        noise_3ch = np.stack([
            noise * (0.9 + np.random.rand() * 0.2),
            noise * (0.9 + np.random.rand() * 0.2),
            noise * (0.9 + np.random.rand() * 0.2)
        ], axis=2)
    else:
        noise_3ch = noise[:, :, np.newaxis]

    result = img_bgr.astype(np.float32) + noise_3ch
    return np.clip(result, 0, 255).astype(np.uint8)


def _paper_texture(img_bgr: np.ndarray, texture_type: str = "glossy") -> np.ndarray:
    """纸基纹理：光面/绸纹/绒面（微结构叠加，10%强度）"""
    if texture_type not in ("silk", "matte", "velvet"):
        return img_bgr
    h, w = img_bgr.shape[:2]
    base = np.zeros((h, w), dtype=np.float32)
    if texture_type == "silk":  # 绸纹：细密波浪纹理
        x = np.linspace(0, 1, w)[np.newaxis, :]
        y = np.linspace(0, 1, h)[:, np.newaxis]
        wave = np.sin(x * 120 + y * 30) * 0.4 + np.sin(x * 70 - y * 60) * 0.3
        base = wave * 6.0
    elif texture_type == "velvet":  # 绒面：大颗粒絮状纹理
        noise_big = cv2.GaussianBlur(
            np.random.rand(h // 8, w // 8).astype(np.float32) * 2 - 1, (5, 5), 0
        )
        base = cv2.resize(noise_big, (w, h)) * 10.0
    elif texture_type == "matte":  # 半光/哑光：均匀细微纹理
        base = (np.random.rand(h, w).astype(np.float32) - 0.5) * 5.0

    if len(img_bgr.shape) == 3:
        base = base[:, :, np.newaxis]
    result = img_bgr.astype(np.float32) + base
    return np.clip(result, 0, 255).astype(np.uint8)


def _highlight_atomize(img_bgr: np.ndarray, strength: float = 0.1) -> np.ndarray:
    """高光雾化：相纸老化的光散射效果（亮部轻微柔光）"""
    if strength <= 0:
        return img_bgr
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    highlight_mask = np.clip((gray - 0.55) * 2.2, 0, 1)[:, :, np.newaxis]
    blur = cv2.GaussianBlur(img_bgr.astype(np.float32), (0, 0), 3.5)
    blend = img_bgr.astype(np.float32) * (1 - strength * highlight_mask) + blur * strength * highlight_mask
    return np.clip(blend, 0, 255).astype(np.uint8)


def _shadow_lift(img_bgr: np.ndarray, gamma_boost: float = 0.2) -> np.ndarray:
    """暗部层次提亮（人相胶片强项：保留毛衣/衬衣针脚纹理）"""
    if gamma_boost <= 0:
        return img_bgr
    img_f = img_bgr.astype(np.float32) / 255.0
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    shadow_mask = np.clip(1.0 - (gray - 0.2) / 0.4, 0, 1)[:, :, np.newaxis]
    boosted = np.power(img_f, 1.0 / (1.0 + gamma_boost))
    blend = img_f * (1 - shadow_mask) + boosted * shadow_mask
    return np.clip(blend * 255.0, 0, 255).astype(np.uint8)


def _add_vignette(img_bgr: np.ndarray, strength: float) -> np.ndarray:
    if strength >= 1.0:
        return img_bgr
    h, w = img_bgr.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    mask = 1 - (dist / max_dist) * (1 - strength)
    mask = mask ** 1.8
    if len(img_bgr.shape) == 3:
        mask = mask[:, :, np.newaxis]
    result = img_bgr.astype(np.float32) * mask
    return np.clip(result, 0, 255).astype(np.uint8)


def _add_cinemascope(img_bgr: np.ndarray, aspect_ratio: str = "2.35:1") -> np.ndarray:
    ratio_parts = aspect_ratio.split(":")
    ratio = float(ratio_parts[0]) / float(ratio_parts[1])
    h, w = img_bgr.shape[:2]
    target_h = int(w / ratio)
    if target_h >= h:
        return img_bgr
    bar_h = (h - target_h) // 2
    result = img_bgr.copy()
    result[:bar_h, :] = 0
    result[-bar_h:, :] = 0
    return result


def _threshold_binary(img_bgr: np.ndarray, threshold: Optional[int] = None) -> np.ndarray:
    """印刷制版片：二值化倾向（极高反差）"""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    if threshold is None:
        threshold, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, bw = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)


def _paper_yellow_tint(img_bgr: np.ndarray, strength: float = 0.12) -> np.ndarray:
    """纸基黄化：米黄纸基高光叠加（L通道在高光区偏暖）"""
    if strength <= 0:
        return img_bgr
    img_f = img_bgr.astype(np.float32) / 255.0
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    # 高光区权重曲线
    mask = np.clip((gray - 0.35) * 1.8, 0, 1)[:, :, np.newaxis]
    tint = np.array([0.90, 0.96, 1.0], dtype=np.float32).reshape(1, 1, 3)  # BGR 顺序，对应米黄
    blended = img_f * (1 - mask * strength) + (img_f * tint) * (mask * strength)
    return np.clip(blended * 255.0, 0, 255).astype(np.uint8)


def _edge_yellow_fade(img_bgr: np.ndarray, strength: float = 0.15) -> np.ndarray:
    """
    边缘米黄渐变褪色（新算法④）：样片13琵琶合影底部/样片11左上角有典型的边缘斑驳黄化
    - 离图像边缘越近 → 褪色越明显；四周（特别是四角）权重最高
    - 褪色色 = 公元彩纸/黑白纸的氧化米黄色
    """
    if strength <= 0:
        return img_bgr
    h, w = img_bgr.shape[:2]
    img_f = img_bgr.astype(np.float32) / 255.0

    # 构造四周边缘权重：x 方向 & y 方向，各取离边最近距离
    x = np.linspace(0, 1, w)[np.newaxis, :]
    y = np.linspace(0, 1, h)[:, np.newaxis]
    x_dist = np.minimum(x, 1.0 - x) * 2.0  # 0=边缘，1=中心
    y_dist = np.minimum(y, 1.0 - y) * 2.0
    edge_mask = 1.0 - np.minimum(x_dist, y_dist)
    edge_mask = np.clip(edge_mask * 1.4, 0, 1) ** 1.6
    edge_mask = edge_mask[:, :, np.newaxis]

    # 彩卷/黑白通用的氧化米黄（BGR: 约 215, 232, 250）
    fade_color = np.array([0.84, 0.91, 0.98], dtype=np.float32).reshape(1, 1, 3)
    blended = img_f * (1 - edge_mask * strength) + (img_f * fade_color) * (edge_mask * strength)
    return np.clip(blended * 255.0, 0, 255).astype(np.uint8)


def _fine_scratches(img_bgr: np.ndarray, density: float = 0.30) -> np.ndarray:
    """
    老照片细划痕（新算法⑤）：样片12仙鹤左下角、样片11左上角边缘有发丝状细划痕
    density: 0~1，划痕数量占比
    """
    if density <= 0:
        return img_bgr
    h, w = img_bgr.shape[:2]
    result = img_bgr.copy()

    # 划痕数量：按面积估算，密度0.3 ≈ 3-8 根（根据尺寸缩放）
    area = h * w
    base_count = int(area / 180000 * density * 10)
    n_scratches = max(1, min(12, base_count + np.random.randint(1, 4)))

    for _ in range(n_scratches):
        # 长度 = 图像短边的 8%~25%
        min_side = min(h, w)
        length = int(min_side * (0.08 + np.random.rand() * 0.17))

        # 起点（偏向边缘，划痕常出现在边缘区域）
        if np.random.rand() < 0.55:
            # 靠近四边之一
            side = np.random.choice(['top', 'bottom', 'left', 'right'])
            margin = int(min_side * 0.03)
            if side == 'top':
                sx, sy = np.random.randint(margin, w - margin), np.random.randint(0, margin + 1)
            elif side == 'bottom':
                sx, sy = np.random.randint(margin, w - margin), np.random.randint(h - margin - 1, h)
            elif side == 'left':
                sx, sy = np.random.randint(0, margin + 1), np.random.randint(margin, h - margin)
            else:
                sx, sy = np.random.randint(w - margin - 1, w), np.random.randint(margin, h - margin)
        else:
            sx, sy = np.random.randint(0, w), np.random.randint(0, h)

        # 方向：偏水平/偏垂直都有，±25°
        angle = np.random.uniform(-np.pi / 2, np.pi / 2)
        if np.random.rand() < 0.5:
            angle += np.pi  # 另一半方向
        dx = int(np.cos(angle) * length)
        dy = int(np.sin(angle) * length)
        ex, ey = sx + dx, sy + dy

        # 颜色：85%概率暗划痕（灰/黑），15%概率亮划痕（白/银盐脱落）
        if np.random.rand() < 0.85:
            scratch_val = int(40 + np.random.rand() * 80)  # 40~120 深灰
            blend_a = 0.25 + np.random.rand() * 0.25
        else:
            scratch_val = int(190 + np.random.rand() * 50)  # 190~240 亮白
            blend_a = 0.20 + np.random.rand() * 0.20

        # 粗细：1px 或 2px，发丝状
        thickness = 1 if np.random.rand() < 0.75 else 2

        # 用透明层叠加，避免直接覆盖
        overlay = result.copy()
        cv2.line(overlay, (sx, sy), (ex, ey), (scratch_val, scratch_val, scratch_val), thickness, lineType=cv2.LINE_AA)
        cv2.addWeighted(overlay, blend_a, result, 1.0 - blend_a, 0, dst=result)

        # 25%概率旁边再来一根更细的伴生划痕（老照片划痕常成对）
        if np.random.rand() < 0.25:
            s2_x = sx + int(np.random.uniform(-5, 5))
            s2_y = sy + int(np.random.uniform(-5, 5))
            length2 = int(length * (0.3 + np.random.rand() * 0.5))
            e2x = s2_x + int(np.cos(angle + np.random.uniform(-0.15, 0.15)) * length2)
            e2y = s2_y + int(np.sin(angle + np.random.uniform(-0.15, 0.15)) * length2)
            cv2.line(result, (s2_x, s2_y), (e2x, e2y), (scratch_val, scratch_val, scratch_val), 1, lineType=cv2.LINE_AA)

    return result


def _highlight_rolloff(img_bgr: np.ndarray, strength: float = 0.18) -> np.ndarray:
    """
    高光滚降（新算法①）：S型压缩曲线，让耳环/戒指/牙齿/花朵高光不溢出死白
    对应样片6（耳环、花朵高光）、样片8（牙齿高光）、样片9（西装驳领反光）
    """
    if strength <= 0:
        return img_bgr
    img_f = img_bgr.astype(np.float32) / 255.0
    # 高光区权重：灰度 > 0.62 的区域逐渐介入
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    mask = np.clip((gray - 0.62) / (1.0 - 0.62), 0, 1) ** 1.2
    mask = mask[:, :, np.newaxis]
    # S型压缩：y = 1 - (1 - x) ^ k，k > 1 让高光滚降更柔和
    k = 1.0 + strength * 3.5  # strength 0.18 → k ≈ 1.63
    compressed = 1.0 - np.power(np.clip(1.0 - img_f, 1e-6, 1.0), k)
    blended = img_f * (1 - mask) + compressed * mask
    return np.clip(blended * 255.0, 0, 255).astype(np.uint8)


def _soft_diffusion(img_bgr: np.ndarray, strength: float = 0.12, radius: float = 5.0) -> np.ndarray:
    """
    柔光半透（新算法②）：高斯模糊层 × 正片叠底混合，模拟丝巾半透明/人相发梢羽化
    对应样片6/8：薄纱丝巾透光可见手轮廓、样片6花朵花瓣半透明、样片9西装面料柔光
    """
    if strength <= 0:
        return img_bgr
    img_f = img_bgr.astype(np.float32)
    blur = cv2.GaussianBlur(img_f, (0, 0), radius).astype(np.float32)
    # 「屏幕+柔光」混合模式的轻量版：原图×0.88 + 模糊×0.12，保留清晰度且有半透感
    blend = img_f * (1 - strength) + blur * strength
    return np.clip(blend, 0, 255).astype(np.uint8)


def _air_perspective(img_bgr: np.ndarray, strength: float = 0.10) -> np.ndarray:
    """
    空气透视雾感（新算法③）：远景/亮部区域叠加轻微灰雾，模拟样片10桂林山水远山雾感
    样片10：远山有天然雾化灰阶（非死白/死黑），近景水草/洗衣人清晰，中景倒影柔和
    """
    if strength <= 0:
        return img_bgr
    h, w = img_bgr.shape[:2]
    img_f = img_bgr.astype(np.float32) / 255.0
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    # 距离+亮度双权重：图像上半部（远景）+ 亮度中段 → 加雾
    y_coord = np.linspace(0, 1, h)[:, np.newaxis]
    dist_weight = y_coord ** 1.6  # 上半部分权重高（约前1/3高度）
    # 最亮的天空+中灰的远山：权重呈倒U型
    brightness_weight = np.exp(-((gray - 0.52) ** 2) / 0.12)
    mask = (dist_weight * 0.55 + brightness_weight * 0.45) * strength
    mask = mask[:, :, np.newaxis]
    # 灰雾色：轻微冷灰（样片10天空是微冷的灰雾）
    fog_color = np.array([228, 232, 234], dtype=np.float32).reshape(1, 1, 3) / 255.0  # BGR
    blended = img_f * (1 - mask) + fog_color * mask
    return np.clip(blended * 255.0, 0, 255).astype(np.uint8)


def _draw_era_logo(pil_img: "Image.Image", border_ratio: float = 0.07, is_grayscale: bool = False):
    """
    「公元」印章暗记（**优先用用户提供的PNG原图，不再自己重绘**）：
    - 从 backend/assets/seal_red.png 或 seal_black.png 读取（去除背景的透明PNG）
    - 文件存在 → 按印章缩放后直接 paste（用alpha通道做mask，完美贴合）
    - 文件不存在 → 兜底：调用旧的手绘逻辑（不报错，保证功能可用）
    - border_ratio 默认 0.07（照片高度的7%）
    """
    if border_ratio <= 0:
        return pil_img
    w, h = pil_img.size
    border_h = max(36, int(h * border_ratio))
    new_h = h + border_h

    canvas = Image.new("RGB", (w, new_h), (248, 245, 235))  # 恢复为米黄色背景栏（取消纯白色修改）
    canvas.paste(pil_img, (0, 0))

    # ===== 印章目标尺寸 & 位置 =====
    seal_w = min(int(border_h * 2.4), int(w * 0.40))
    seal_h = min(int(border_h * 0.95), int(w * 0.17))
    left_margin = int(w * 0.07)
    seal_cy = h + border_h // 2
    seal_x1 = left_margin
    seal_y1 = seal_cy - seal_h // 2

    # ===== 找印章 PNG 文件（backend/assets/ 下）
    # 策略（完全按最新要求）：
    #  黑白照 is_grayscale=True：
    #    优先级 1) era_logo_black.png（用户要求的「黑白专用厂标」）
    #    优先级 2) era_logo.png（通用兜底）
    #    优先级 3) 手绘兜底
    #  彩照 is_grayscale=False：
    #    优先级 1) era_logo_red.png（用户指定彩色厂标）
    #    优先级 2) era_logo.png（通用兜底）
    #    优先级 3) 手绘兜底
    _mod_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(_mod_dir, "assets")

    candidates = []
    if is_grayscale:
        # 黑白照：era_logo_black → era_logo 顺序
        blk_path = os.path.join(assets_dir, "era_logo_black.png")
        if os.path.isfile(blk_path):
            candidates.append(("era_logo_black", blk_path))
        era_path = os.path.join(assets_dir, "era_logo.png")
        if os.path.isfile(era_path) and era_path != blk_path:
            candidates.append(("era_logo", era_path))
    else:
        # 彩照：用 era_logo_red.png（用户指定）
        red_path = os.path.join(assets_dir, "era_logo_red.png")
        if os.path.isfile(red_path):
            candidates.append(("era_logo_red", red_path))
        era_path = os.path.join(assets_dir, "era_logo.png")
        if os.path.isfile(era_path) and era_path != red_path:
            candidates.append(("era_logo", era_path))

    _used_png = False
    for name, seal_path in candidates:
        try:
            seal_img = Image.open(seal_path).convert("RGBA")
            src_w, src_h = seal_img.size
            src_ratio = src_w / float(src_h) if src_h > 0 else 2.4
            tgt_ratio = seal_w / float(seal_h) if seal_h > 0 else src_ratio
            if abs(src_ratio - tgt_ratio) > 0.02:
                # 按高度等比缩放，保持印章不拉伸变形
                final_h = seal_h
                final_w = max(1, int(final_h * src_ratio))
            else:
                final_w, final_h = seal_w, seal_h
            final_w = min(final_w, int(w * 0.46))
            seal_resized = seal_img.resize((final_w, final_h), Image.LANCZOS)
            paste_y = seal_cy - final_h // 2
            paste_x = seal_x1
            if seal_resized.mode == "RGBA":
                r, g, b, a = seal_resized.split()
                canvas.paste(seal_resized, (paste_x, paste_y), mask=a)
            else:
                canvas.paste(seal_resized, (paste_x, paste_y))
            _used_png = True
            break
        except Exception:
            _used_png = False
            continue

    if _used_png:
        return canvas

    # ========== FALLBACK：找不到PNG文件时，用手绘兜底（不保证样式100%） ==========
    draw = ImageDraw.Draw(canvas)
    seal_x2 = seal_x1 + seal_w
    seal_y2 = seal_y1 + seal_h
    corner_r = min(10, seal_h // 4)

    if is_grayscale:
        seal_fill = (28, 24, 20)
        seal_stroke = (45, 40, 35)
        text_fill = (248, 245, 235)
        stripe_fill = (70, 62, 54)
    else:
        seal_fill = (200, 16, 42)     # 朱红 #C8102E
        seal_stroke = (148, 12, 30)
        text_fill = (252, 248, 240)
        stripe_fill = (228, 28, 58)

    draw.rounded_rectangle([seal_x1, seal_y1, seal_x2, seal_y2],
                           radius=corner_r, fill=seal_fill, outline=seal_stroke, width=2)
    stripe_w = max(8, int(seal_w * 0.11))
    stripe_h_region = max(6, int(seal_h * 0.18))
    stripe_step = max(3, int(seal_h * 0.11))
    right_x1, right_y1 = seal_x2 - stripe_w, seal_y1 + int(seal_h * 0.05)
    right_x2, right_y2 = seal_x2 - 2, seal_y2 - int(seal_h * 0.05)
    for yy in range(right_y1 - (right_x2 - right_x1), right_y2 + stripe_step, stripe_step):
        draw.line([(right_x1, yy), (right_x2, yy + (right_x2 - right_x1))],
                  fill=stripe_fill, width=2)
    bot_y1, bot_x1 = seal_y2 - stripe_h_region, seal_x1 + int(seal_w * 0.08)
    bot_x2, bot_y2 = seal_x2 - int(seal_w * 0.04), seal_y2 - 2
    for xx in range(bot_x1 - (bot_y2 - bot_y1), bot_x2 + stripe_step, stripe_step):
        draw.line([(xx, bot_y1), (xx + (bot_y2 - bot_y1), bot_y2)],
                  fill=stripe_fill, width=2)

    inner_x1 = seal_x1 + int(seal_w * 0.10)
    inner_x2 = seal_x2 - stripe_w - int(seal_w * 0.02)
    inner_w = inner_x2 - inner_x1
    inner_h = seal_h - int(seal_h * 0.18)
    char_gap = int(inner_w * 0.03)
    char_w = (inner_w - char_gap) // 2
    font_size = max(14, int(inner_h * 0.92))
    font = None
    font_candidates = [
        ("STXingkai.ttf", font_size), ("STKaiti.ttf", font_size),
        ("KaiTi.ttf", font_size), ("KaiTi_GB2312.ttf", font_size),
        ("SimKai.ttf", font_size), ("SimHei.ttf", font_size + 2),
        ("msyh.ttc", font_size + 2),
    ]
    for fname, sz in font_candidates:
        try:
            font = ImageFont.truetype(fname, sz)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    gong_box_x, gong_box_y = inner_x1, seal_y1 + (seal_h - inner_h) // 2
    gong_cx, gong_cy = gong_box_x + char_w // 2, gong_box_y + inner_h // 2
    try:
        bb = draw.textbbox((0, 0), "公", font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        draw.text((gong_cx - tw // 2 - bb[0], gong_cy - th // 2 - bb[1]), "公", fill=text_fill, font=font)
    except Exception:
        draw.text((gong_box_x + char_w * 0.20, gong_box_y + inner_h * 0.05), "公", fill=text_fill, font=font)

    yuan_box_x, yuan_cx = inner_x1 + char_w + char_gap, inner_x1 + char_w + char_gap + char_w // 2
    try:
        bb = draw.textbbox((0, 0), "元", font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        draw.text((yuan_cx - tw // 2 - bb[0], gong_cy - th // 2 - bb[1]), "元", fill=text_fill, font=font)
    except Exception:
        draw.text((yuan_box_x + char_w * 0.15, gong_box_y + inner_h * 0.05), "元", fill=text_fill, font=font)

    return canvas


def apply_film_filter(image_bytes: bytes, params: Dict[str, Any]) -> bytes:
    """
    主滤镜函数：严格按照史料参数执行处理流水线
    处理顺序参考暗房物理流程：曝光→显影（反差/色偏）→定影（饱和/颗粒）→水洗（雾化/黄化）→晾干（纸基/白边）
    """
    pil_img = Image.open(BytesIO(image_bytes)).convert("RGB")
    p = params

    # 0. 转 BGR（OpenCV 约定）
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 1. 反差 alpha·x + beta（史料级核心公式）
    if p.get("contrast_alpha") is not None or p.get("contrast_beta", 0) != 0:
        alpha = p.get("contrast_alpha", 1.0)
        beta = p.get("contrast_beta", 0)
        img = _contrast_alpha_beta(img, alpha, beta)
    elif p.get("contrast", 1.0) != 1.0:
        # 兼容旧字段
        img = _contrast_alpha_beta(img, p["contrast"], 0)

    # 2. 通道级色偏偏移（史料：R+15, B-8）
    img = _channel_shift_bgr(
        img,
        r_delta=p.get("r_shift", 0),
        g_delta=p.get("g_shift", 0),
        b_delta=p.get("b_shift", 0)
    )

    # 3. 黑白转换（如需）
    if p.get("grayscale"):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 4. 饱和度（彩卷专用）
    sat = p.get("saturation")
    if sat is not None and sat != 1.0 and not p.get("grayscale"):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat, 0, 255)
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # 5. 锐化 / USM
    usm_amount = p.get("usm_amount", 0)
    if usm_amount > 0:
        radius = p.get("usm_radius", 1.0)
        blur = cv2.GaussianBlur(img, (0, 0), max(0.5, radius))
        img = np.clip(img.astype(np.float32) * (1 + usm_amount) - blur.astype(np.float32) * usm_amount,
                      0, 255).astype(np.uint8)
    elif p.get("sharpness") is not None and p["sharpness"] != 1.0:
        # 兼容旧字段
        pil_mid = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pil_mid = ImageEnhance.Sharpness(pil_mid).enhance(p["sharpness"])
        img = cv2.cvtColor(np.array(pil_mid), cv2.COLOR_RGB2BGR)

    # 6. 暗部层次提亮（人相胶片、印相纸）
    img = _shadow_lift(img, p.get("shadow_lift", 0.0))

    # 7. 高光雾化（相纸老化光散射）
    img = _highlight_atomize(img, p.get("highlight_fog", 0.0))

    # 7b. 高光滚降（新算法①：耳环/戒指/花朵/牙齿高光不死白，样片6-9）
    img = _highlight_rolloff(img, p.get("highlight_rolloff", 0.0))

    # 7c. 柔光半透（新算法②：丝巾半透明/人相发梢羽化，样片6/8/9）
    img = _soft_diffusion(img,
                          strength=p.get("soft_diffusion", 0.0),
                          radius=p.get("soft_diffusion_radius", 5.0))

    # 7d. 空气透视雾感（新算法③：远山天然雾化，样片10桂林山水）
    img = _air_perspective(img, p.get("air_perspective", 0.0))

    # 8. 色温/整体色罩
    if p.get("tint") and p.get("tint_strength", 0) > 0:
        tint_bgr = [p["tint"][2], p["tint"][1], p["tint"][0]]  # RGB → BGR
        tint_arr = np.array(tint_bgr, dtype=np.float32).reshape(1, 1, 3)
        blended = img.astype(np.float32) * (1 - p["tint_strength"]) + tint_arr * p["tint_strength"]
        img = np.clip(blended, 0, 255).astype(np.uint8)

    # 9. 纸基黄化（印相纸、老照片）
    img = _paper_yellow_tint(img, p.get("paper_yellow", 0.0))

    # 9b. 边缘米黄渐变褪色（新算法④：样片13底部/样片11四角的氧化斑驳）
    img = _edge_yellow_fade(img, p.get("edge_yellow_fade", 0.0))

    # 10. 轻微褪色（fading effect，彩卷老照片）
    if p.get("fade", 0) > 0:
        fade = p["fade"]
        img = img.astype(np.float32) * (1 - fade) + 128 * fade
        img = np.clip(img, 0, 255).astype(np.uint8)

    # 11. 二值化（印刷制版片）
    if p.get("binary_threshold"):
        img = _threshold_binary(img, None if p["binary_threshold"] is True else p["binary_threshold"])

    # 12. 银盐颗粒
    img = _silver_grain(img, p.get("grain_sigma", 0.0), p.get("content_aware_grain", True))

    # 12b. 老照片细划痕（新算法⑤：样片12左下角/样片11边缘的发丝状划痕）
    img = _fine_scratches(img, p.get("fine_scratches", 0.0))

    # 13. 纸基纹理（印相纸）
    if p.get("paper_texture"):
        img = _paper_texture(img, p["paper_texture"])

    # 14. 暗角
    img = _add_vignette(img, p.get("vignette", 1.0))

    # 15. 电影宽幅黑边
    if p.get("cinemascope"):
        img = _add_cinemascope(img, p.get("aspect_ratio", "2.35:1"))

    # 转 PIL 做白边暗记
    result_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # 16. 哑光效果（印相纸）
    if p.get("matte"):
        result_pil = ImageOps.posterize(result_pil, 5)
        result_pil = result_pil.filter(ImageFilter.SMOOTH)

    # 17. 「公元」印章白边暗记
    if p.get("add_border_logo", True):
        result_pil = _draw_era_logo(
            result_pil,
            border_ratio=p.get("border_ratio", 0.07),
            is_grayscale=p.get("grayscale", False)
        )

    buf = BytesIO()
    result_pil.save(buf, format="JPEG", quality=93)
    return buf.getvalue()
