FILMS = {

    # ==========================================
    # 01. 公元黑白胶卷 1980s（135/120 全色负片）
    # 史料依据：1958年投产，1981年获国家银牌，GB21°=ISO100
    # ==========================================
    "film_001": {
        "id": "film_001",
        "name": "公元黑白胶卷 1980s",
        "short_name": "黑白胶卷",
        "era": "1980年代",
        "category": "黑白胶卷",
        "category_icon": "🎞️",
        "keywords": ["80年代", "黑白", "复古", "银盐颗粒", "高对比", "怀旧", "135胶卷", "120胶卷"],
        "filter_params": {
            "grayscale": True,
            "contrast_alpha": 1.27,
            "contrast_beta": 4,
            "r_shift": 3,
            "g_shift": 1,
            "b_shift": -2,
            "grain_sigma": 10.0,
            "content_aware_grain": True,
            "shadow_lift": 0.15,
            "highlight_fog": 0.07,
            "highlight_rolloff": 0.15,
            "air_perspective": 0.10,
            "paper_yellow": 0.08,
            "vignette": 0.78,
            "usm_amount": 0.2,
            "usm_radius": 0.8,
            "add_border_logo": True,
            "border_ratio": 0.07,
            "edge_yellow_fade": 0.10,
            "fine_scratches": 0.25
        },
        "story": {
            "title": "改革开放的银盐记忆",
            "content": "1958年，汕头公元感光材料厂的第一卷黑白胶卷走下生产线。在此之前，中国人用的胶卷全部依赖进口——柯达叫'矮克发'，富士叫'樱花牌'，一卷胶卷抵得上普通工人一周口粮。1981年，公元黑白胶卷拿下国家银质奖章，从此成为中国家庭记录人生大事的标配：满月照、毕业照、全家福、探亲团聚……你在任何一本80年代的家庭相册里，都能找到它的影子——那不是黑白，那是一整个朴素而热气腾腾的年代。",
            "fun_fact": "当年的照相馆师傅有三件宝：蒙镜头的薄丝袜（给姑娘拍柔焦）、摇来摇去的上色笔（给黑白照手工上色）、还有嘴边永远的那句：'头往左边一点，笑一下，好！'"
        }
    },

    # ==========================================
    # 02. 公元人相胶片（拳头产品！）
    # 史料依据：1955年试制成功，4寸/6寸大画幅，"没有厂子可以跟我们竞争"
    # ==========================================
    "film_002": {
        "id": "film_002",
        "name": "公元人相胶片（4×5英寸）",
        "short_name": "人相胶片",
        "era": "1955年起",
        "category": "专业人像",
        "category_icon": "👤",
        "keywords": ["人像", "专业", "高解像力", "层次丰富", "细腻", "照相馆", "大画幅", "4寸片", "6寸片"],
        "filter_params": {
            "grayscale": True,
            "contrast_alpha": 1.20,
            "contrast_beta": 3,
            "grain_sigma": 7.0,
            "content_aware_grain": True,
            "shadow_lift": 0.32,
            "highlight_fog": 0.10,
            "highlight_rolloff": 0.28,
            "soft_diffusion": 0.18,
            "soft_diffusion_radius": 5.5,
            "paper_yellow": 0.10,
            "vignette": 0.85,
            "usm_amount": 0.35,
            "usm_radius": 1.0,
            "add_border_logo": True,
            "border_ratio": 0.07,
            "fine_scratches": 0.40,
            "edge_yellow_fade": 0.10
        },
        "story": {
            "title": "照相馆里的拳头产品",
            "content": "1955年4月，工程师林希之在汕头的小作坊里，试制成了中国第一张人像胶片。这是一种4×5英寸的大画幅散页片，专门供给照相馆的木制座机使用。老一辈的公元人骄傲地说：'人像片没有厂子可以跟我们竞争，这是公元的拳头产品。'从建国初的干部标准像，到文革后的第一次结婚登记照，再到80年代的艺术照潮——你祖父母、父母身份证上的那张照片，很大概率就是用公元人像胶片拍的。",
            "fun_fact": "当年照相馆拍完照，师傅会在装底片的牛皮纸袋上手写一行字：'此片拍糊了，印时请修'或'此人左脸有疤，印时请抹去'——这是那个没有Photoshop的年代，暗房师傅的'PS备注'。"
        }
    },

    # ==========================================
    # 03. 公元彩色负片 1985（彩卷！）
    # 史料依据：1984-85年进口富士大轴分装，年产200-300万卷还供不应求
    # ==========================================
    "film_003": {
        "id": "film_003",
        "name": "公元彩色负片 1985",
        "short_name": "彩色胶卷",
        "era": "1980年代中",
        "category": "彩色胶卷",
        "category_icon": "🎨",
        "keywords": ["90年代", "彩色", "暖色调", "褪色", "怀旧", "家庭相册", "红黄鲜艳", "绿偏旧", "富士大轴"],
        "filter_params": {
            "grayscale": False,
            "contrast_alpha": 0.92,
            "contrast_beta": 10,
            "r_shift": 12,
            "g_shift": 5,
            "b_shift": -11,
            "saturation": 0.62,
            "grain_sigma": 5.0,
            "content_aware_grain": True,
            "shadow_lift": 0.10,
            "highlight_fog": 0.12,
            "highlight_rolloff": 0.12,
            "soft_diffusion": 0.06,
            "air_perspective": 0.06,
            "paper_yellow": 0.10,
            "fade": 0.08,
            "vignette": 0.82,
            "add_border_logo": True,
            "border_ratio": 0.07,
            "edge_yellow_fade": 0.15,
            "fine_scratches": 0.20
        },
        "story": {
            "title": "一盒彩卷，三天工资",
            "content": "1984年的汕头公元厂，第一次从日本富士买进了整箱的彩色胶卷'大轴'——就是那种一人高、几公里长的母卷。工人们在恒温恒湿的暗房里，把它分切、装卷、贴标签，一卷卷打上'公元牌彩色胶卷'的包装。那时一盒彩卷带冲印要三十多块，相当于普通工人三天的工资。尽管贵，1985年的产量还是达到了三百万卷，并且供不应求。中国老百姓终于不用再只拍黑白照了，春游、生日宴、第一次去北京天安门，都变成了带颜色的记忆。",
            "fun_fact": "当年的彩卷广告写着：'胶卷选公元，色彩自然鲜。'而使用说明的第一条永远是：'请于拍摄后六个月内冲洗，存放过久将产生褪色偏紫。'——没错，你今天看到的90年代老照片偏紫，不是错觉，是写进说明书的。"
        }
    },

    # ==========================================
    # 04. 公元彩色反转片（幻灯片）
    # 史料依据：1980年代末，油溶性，影调饱和鲜艳，色牢度好
    # ==========================================
    "film_004": {
        "id": "film_004",
        "name": "公元彩色反转片（幻灯片）",
        "short_name": "反转片",
        "era": "1980年代末",
        "category": "专业彩色",
        "category_icon": "🔮",
        "keywords": ["幻灯片", "反转片", "油溶性", "色彩艳丽", "饱和", "通透", "投影", "放映", "高反差"],
        "filter_params": {
            "grayscale": False,
            "contrast_alpha": 1.20,
            "contrast_beta": -5,
            "r_shift": 4,
            "g_shift": 1,
            "b_shift": 2,
            "saturation": 1.25,
            "grain_sigma": 3.0,
            "content_aware_grain": True,
            "vignette": 0.82,
            "highlight_rolloff": 0.08,
            "usm_amount": 0.5,
            "usm_radius": 1.0,
            "add_border_logo": True,
            "border_ratio": 0.07
        },
        "story": {
            "title": "拉上窗帘，开幻灯机",
            "content": "彩色反转片，又叫'幻灯片'——拍出来的底片不是负像，而是正像。对着灯光看，每一张都通透得像彩色玻璃。1980年代末，公元引进油溶性工艺生产反转片，解决了早期水溶性反转片'见光掉色'的问题。当年的大学阶梯教室、单位会议室、旅行社的线路说明会……拉上窗帘、架起幻灯机、咔哒一声切换下一张——那是 PowerPoint 出现之前，中国人最着迷的'沉浸式放映体验'。",
            "fun_fact": "反转片有个吓人的外号叫'废片杀手'：曝光差半档，整张就废了。所以专业摄影师拍反转片时，会围着同个景用不同曝光连拍3张——这叫'包围曝光'，只求有一张能用。"
        }
    },

    # ==========================================
    # 05. 公元彩色电影正片 1970s
    # 史料依据：1971-74年研制成功，北影拷贝后效果与伊士曼无明显差别
    # ==========================================
    "film_005": {
        "id": "film_005",
        "name": "公元彩色电影正片 1970s",
        "short_name": "电影胶片",
        "era": "1973年",
        "category": "电影胶片",
        "category_icon": "🎬",
        "keywords": ["70年代", "电影", "宽幅", "暖橙", "放映机", "露天电影", "油溶性", "拷贝", "35mm"],
        "filter_params": {
            "grayscale": False,
            "contrast_alpha": 1.15,
            "contrast_beta": 0,
            "r_shift": 10,
            "g_shift": 3,
            "b_shift": -4,
            "saturation": 1.30,
            "grain_sigma": 3.0,
            "content_aware_grain": True,
            "vignette": 0.68,
            "highlight_fog": 0.05,
            "highlight_rolloff": 0.10,
            "air_perspective": 0.08,
            "cinemascope": True,
            "aspect_ratio": "2.35:1",
            "add_border_logo": False,
            "border_ratio": 0.0
        },
        "story": {
            "title": "露天上演的彩色奇迹",
            "content": "1973年，全国电影工作会议现场，北京电影制片厂用公元牌油溶性彩色电影正片印出来的拷贝，投放到了大银幕上。专家们看完后一致给出评价：'与美国伊士曼柯达胶片相比，没有明显差别。'同年，这款胶片拿下了'全国科学大会优秀科技成果奖'。1970年代的夏夜，村口的晒谷场架起白布，放映员手摇发电机启动，公元电影胶片在放映机里咔哒咔哒地转动——那是整个村子一年中最热闹的夜晚。",
            "fun_fact": "公元电影胶片每米长有16帧画面，一部90分钟的电影要拷贝5卷，总重近百斤。放映员骑着自行车驮着铁盒翻山越岭，盒子上用红漆写着八个字：'电影拷贝，小心轻放'。"
        }
    },

    # ==========================================
    # 06. 公元X光胶片
    # 史料依据：蓝黑色影像，极高反差（alpha=2.5），无灰阶，极度锐利，天津产
    # ==========================================
    "film_006": {
        "id": "film_006",
        "name": "公元X光胶片（医用/工业）",
        "short_name": "X光胶片",
        "era": "1960-90年代",
        "category": "特种胶片",
        "category_icon": "🦴",
        "keywords": ["X光", "医用", "工业", "蓝黑", "高反差", "透视", "无损检测", "冷峻", "赛博朋克", "青蓝调"],
        "filter_params": {
            "grayscale": False,
            "contrast_alpha": 2.50,
            "contrast_beta": 0,
            "r_shift": -30,
            "g_shift": -10,
            "b_shift": 20,
            "grain_sigma": 0.0,
            "content_aware_grain": False,
            "usm_amount": 1.2,
            "usm_radius": 0.6,
            "add_border_logo": True,
            "border_ratio": 0.07,
            "tint": [160, 200, 230],
            "tint_strength": 0.18
        },
        "story": {
            "title": "透视真相的蓝黑底片",
            "content": "很多人不知道，公元厂除了民用胶卷，还是中国医用和工业X光胶片的核心供应商。这种胶片采用蓝色片基，感光乳剂涂布在片基的正反两面——这样才能在X光的短波射线下捕捉到钢板的裂纹、人体的骨骼。1960-90年代，国内医院的每一张胸片、每一张骨科透视片；航空航天工厂里每一块机翼铸件的无损检测；造船厂每一道焊缝的内部检查——几乎都印着公元的牌子。它不记录美，它记录结构、裂纹和真相。",
            "fun_fact": "X光胶片拍完后不能见光，要在完全黑暗或暗红色安全灯下冲洗。当年的暗房师傅开玩笑说：'拍X光片跟做贼似的，全程摸黑干，干完活衣服上全是醋酸味儿。'"
        }
    },

    # ==========================================
    # 07. 公元印刷制版胶片
    # 史料依据：1963-64年研制成功，国家优秀新产品三等奖，8个配套品种
    # ==========================================
    "film_007": {
        "id": "film_007",
        "name": "公元印刷制版胶片（PB中性全色）",
        "short_name": "制版胶片",
        "era": "1964年",
        "category": "工业印刷",
        "category_icon": "🖨️",
        "keywords": ["制版", "印刷", "二值化", "极高反差", "黑白分明", "线条清晰", "网点", "报纸", "PB中性片"],
        "filter_params": {
            "grayscale": True,
            "contrast_alpha": 3.0,
            "contrast_beta": -50,
            "grain_sigma": 0.0,
            "content_aware_grain": False,
            "binary_threshold": True,
            "usm_amount": 0.8,
            "usm_radius": 0.5,
            "add_border_logo": True,
            "border_ratio": 0.07
        },
        "story": {
            "title": "没有它，印不出一张报纸",
            "content": "1964年，第一届全国新产品展览会，公元牌PB中性全色制版胶片拿下了国家级奖项。在此之前，印刷制版胶片全靠进口，一张大报的付印，可能因为缺几张胶片而延期。印刷制版片是'黑白分明'到了极致的东西——它的反差极高，只有纯黑和纯白，没有任何灰阶。报纸上的照片、书上的插图、烟盒上的图案——所有印刷品，都必须先用制版胶片拍出'网点底片'，才能上印刷机。它是整个中国出版业的幕后英雄。",
            "fun_fact": "制版胶片拍出来的文字必须'一根头发丝都不能糊'，否则印出来的报纸字会发毛。检验员用10倍放大镜挑毛病：'这个字的右下角多了个黑点，重拍！'——比语文老师改作文还严。"
        }
    },

    # ==========================================
    # 08. 公元黑白印相纸（1号软/2号正常/3号硬/4号特硬 + 光/绸/绒 纸面）
    # 史料依据：1952年第一张符合要求的相纸，1985年年产120.9万盒
    # ==========================================
    "film_008": {
        "id": "film_008",
        "name": "公元黑白印相纸（2号·绸纹）",
        "short_name": "印相纸",
        "era": "1952年起",
        "category": "相纸类",
        "category_icon": "📜",
        "keywords": ["印相纸", "放大纸", "绸纹", "光面", "绒面", "暖黑", "米黄纸基", "暗房", "手工冲印", "铂金调", "1号软", "2号正常", "3号硬", "4号特硬"],
        "filter_params": {
            "grayscale": True,
            "contrast_alpha": 1.0,
            "contrast_beta": 0,
            "grain_sigma": 2.0,
            "content_aware_grain": False,
            "shadow_lift": 0.12,
            "highlight_fog": 0.14,
            "highlight_rolloff": 0.20,
            "soft_diffusion": 0.08,
            "soft_diffusion_radius": 4.5,
            "paper_yellow": 0.16,
            "paper_texture": "silk",
            "vignette": 0.92,
            "matte": False,
            "add_border_logo": True,
            "border_ratio": 0.09,
            "edge_yellow_fade": 0.18,
            "fine_scratches": 0.30
        },
        "story": {
            "title": "暗房红灯下的温暖奇迹",
            "content": "1952年，汕头公元的实验室里诞生了中国第一张符合使用要求的黑白相纸。在此之前，暗房用的相纸全是德国产的'矮克发'和英国产的'伊尔福'。公元印相纸分四个反差等级：1号（软，适合层次丰富的人像）、2号（正常，绝大多数场景）、3号（硬，风景文档）、4号（特硬，线条图表）。纸基又分光面、绸纹、绒面、半光四种——当年的姑娘们最爱绸纹纸，因为'脸上的小颗粒看不见，显得皮肤好'。1985年，公元相纸的年产量达到了120.9万盒，能绕地球大半圈。",
            "fun_fact": "暗房里的红灯下，相纸'见红光不死、见白光就废'。师傅们有个行规：洗照片不许聊天，据说情绪会让手发抖，也会影响显影液温度——暗房里永远安静，只有流水声和镊子碰盘子的叮当。"
        },
        "variants_note": "印相纸支持4档反差+3种纸面：如需切换，可在custom_params中覆盖：\n· 反差：contrast_alpha+contrast_beta → 1号(0.85/5) 2号(1.0/0) 3号(1.25/-5) 4号(1.5/-10)\n· 纸面：paper_texture → glossy光面(默认不加)/silk绸纹/velvet绒面/matte半光"
    }
}


VARIANT_PRESETS = {
    "film_008_1s": {
        "desc": "印相纸1号软·绸纹（人像/柔和）",
        "override": {"contrast_alpha": 0.85, "contrast_beta": 5, "paper_texture": "silk"}
    },
    "film_008_3v": {
        "desc": "印相纸3号硬·绒面（风景/质感）",
        "override": {"contrast_alpha": 1.25, "contrast_beta": -5, "paper_texture": "velvet"}
    },
    "film_008_4g": {
        "desc": "印相纸4号特硬·光面（文档/线条）",
        "override": {"contrast_alpha": 1.5, "contrast_beta": -10, "paper_texture": "matte", "usm_amount": 0.6}
    }
}


def match_film_by_keywords(user_input: str) -> str:
    """基于关键词的硬规则匹配（兜底用，不依赖LLM）"""
    if not user_input:
        return "film_001"
    input_lower = user_input.lower()

    # 强匹配：命中某些关键字直接返回
    direct_map = [
        (["人像", "人物", "脸", "写真", "证件照", "照相馆"], "film_002"),
        (["彩色", "彩卷", "彩照", "暖黄", "褪色", "90", "九十", "相册", "家庭"], "film_003"),
        (["反转", "幻灯", "投影", "透明", "通透", "饱和", "鲜艳"], "film_004"),
        (["电影", "宽幅", "银幕", "放映", "拷贝", "70", "七十", "露天"], "film_005"),
        (["x光", "x光", "透视", "骨骼", "医用", "工业", "检测", "蓝", "青蓝", "赛博", "冷峻"], "film_006"),
        (["制版", "印刷", "报纸", "网点", "线条", "黑白分明", "二值"], "film_007"),
        (["相纸", "印相", "放大纸", "绸纹", "光面", "绒面", "纸基", "暗房", "手工", "铂金", "暖棕"], "film_008"),
        (["黑白", "胶卷", "135", "120", "80", "八十", "怀旧", "颗粒", "复古"], "film_001"),
    ]
    for kws, fid in direct_map:
        for kw in kws:
            if kw.lower() in input_lower:
                return fid

    # 弱匹配：积分制
    scores = {}
    for film_id, film in FILMS.items():
        score = 0
        for kw in film["keywords"]:
            if kw.lower() in input_lower:
                score += 2
        if film["era"].replace("年代", "") in user_input:
            score += 3
        if film["category"] in user_input:
            score += 2
        scores[film_id] = score

    if max(scores.values()) == 0:
        return "film_001"
    return max(scores, key=scores.get)
