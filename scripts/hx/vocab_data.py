"""
hx.vocab_data — Rich, genuinely differentiated specifications & 75 authentic sample
vocabulary entries (5 themes × 15 words) for the Chiikawa Vocabulary Tracker Suite (#96–#100):
  #96  Chiikawa Strawberry Milk  -> SRS 5-Step Spaced Repetition (1-3-7-14-30d)
  #97  Hachiware Sky Study       -> IELTS / TOEIC Academic (Band, Collocations, Synonyms)
  #98  Usagi Honey Flashcard     -> 2-Way Quiz Mode + Speaking Phrasal Verbs & Idioms
  #99  Momonga Lavender Media    -> Multi-Language Immersion via Movies / Songs / Podcasts
  #100 Shisa Matcha Bookshop     -> Exam Sprint Countdown & Confusing-Pairs Mistake Bank
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VocabThemeDef:
    num: int
    stem: str
    short_key: str
    slug: str
    char_name: str
    title_en: str
    subtitle_vi: str
    emoji: str
    mode: str  # "srs" | "ielts" | "flashcard" | "media" | "exam"
    # Palette (hex)
    primary: str
    primary_dark: str
    soft: str
    page: str
    card: str
    ink: str
    muted: str
    line: str
    on_primary: str
    accent_alt: str
    warn_fill: str
    warn_ink: str
    # Whitelist v4.2 Typography
    font_display: str
    font_caps: str
    font_vn: str
    font_num: str
    # Study copy & domain data
    stage_names: tuple[str, ...]
    practice_steps: tuple[str, ...]
    guide_method_title: str
    guide_method_bullets: tuple[str, ...]
    toast_perfect: str
    toast_practice: str
    samples: tuple[tuple, ...] = field(default_factory=tuple)


VOCAB_THEMES: list[VocabThemeDef] = [
    # =========================================================================
    # #96 — CHIIKAWA STRAWBERRY MILK (SRS 5-STEP DAILY VOCAB)
    # =========================================================================
    VocabThemeDef(
        num=96,
        stem="96_Chiikawa_SRS_Daily_Vocab",
        short_key="96_chiikawa_srs_vocab",
        slug="chiikawa_srs_vocab",
        char_name="Chiikawa",
        title_en="CHIIKAWA STRAWBERRY MILK • SRS VOCAB",
        subtitle_vi="Học từ vựng khoa học bằng Lặp lại Ngắt quãng 5 mốc (1 – 3 – 7 – 14 – 30 ngày)",
        emoji="🍓",
        mode="srs",
        primary="#E27192",
        primary_dark="#9E3B5C",
        soft="#FFD6E0",
        page="#FFF9F5",
        card="#FFFFFF",
        ink="#5C4033",
        muted="#8C6D63",
        line="#F3C6D3",
        on_primary="#FFFFFF",
        accent_alt="#F8A8C0",
        warn_fill="#FFE4E6",
        warn_ink="#BE123C",
        font_display="Lucida Handwriting",
        font_caps="Georgia",
        font_vn="Segoe UI",
        font_num="Georgia",
        stage_names=("Mới mở sách", "Khởi động nhẹ", "Chăm chỉ học", "Hiểu bài vui", "Hứng khởi sao", "Thuộc 100%!"),
        practice_steps=(
            "🍓 Mở danh sách từ báo đỏ 'Hôm nay phải ôn!' và tự nhẩm lại nghĩa",
            "✍️ Nạp thêm 5–10 từ vựng giao tiếp mới kèm ví dụ đời sống của riêng mình",
            "🙈 Bật công tắc 'Ẩn Nghĩa' (B11) để tự kiểm tra trí nhớ chủ động",
            "🗣️ Đọc to từng từ kèm phiên âm IPA 3 lần cho chuẩn ngữ điệu",
            "🌸 Tick hoàn thành mốc ôn L1–L5 để Chiikawa tiến hóa rực rỡ!",
        ),
        guide_method_title="🍓  CÁCH HỌC SRS 5 MỐC (1 – 3 – 7 – 14 – 30 NGÀY)",
        guide_method_bullets=(
            "1. Nhập từ mới & ngày bắt đầu học (cột G). File tự tính 'Ngày ôn tiếp theo' theo đúng đường cong quên Ebbinghaus: +1 ngày → +3 → +7 → +14 → +30 ngày.",
            "2. Khi tới hạn ôn, cột Trạng thái tự động bật đỏ '🔴 Hôm nay phải ôn!' và đẩy từ lên bảng ưu tiên ở tab 🎯 Luyện Tập & Lịch Ôn.",
            "3. Mỗi lần ôn nhớ, tick thêm 1 mốc L1 → L5. Khi tick đủ L5 (+30 ngày), từ chuyển sang '🌸 Đã thuộc' vĩnh viễn!",
        ),
        toast_perfect="🍓 Chiikawa khen ngợi! Bạn đã hoàn thành xuất sắc mục tiêu từ vựng SRS hôm nay! ✨",
        toast_practice="🌸 Tuyệt vời! Hoàn thành đủ 5 bước ôn tập SRS cùng Chiikawa rồi nhé!",
        # (word, ipa, meaning, example, days_ago, l1, l2, l3, l4, l5)
        samples=(
            ("serendipity",   "/ˌser.ənˈdɪp.ə.ti/", "Sự tình cờ may mắn kỳ diệu",      "Meeting my best friend at that cafe was pure serendipity.", 32, True,  True,  True,  True,  True),
            ("resilient",     "/rɪˈzɪl.jənt/",      "Kiên cường, mau phục hồi",         "She stayed resilient despite facing tight deadlines.",      31, True,  True,  True,  True,  True),
            ("unwind",        "/ʌnˈwaɪnd/",         "Thư giãn, xả hơi sau giờ làm",     "I love listening to lo-fi music to unwind at night.",       20, True,  True,  True,  True,  False),
            ("mindful",       "/ˈmaɪnd.fəl/",       "Chánh niệm, chú tâm hiện tại",     "Try to be mindful of your breathing when stressed.",        16, True,  True,  True,  False, False),
            ("wholesome",     "/ˈhoʊl.səm/",        "Lành mạnh, ấm áp, tích cực",       "Chiikawa episodes are so wholesome and comforting.",        15, True,  True,  True,  False, False),
            ("spontaneous",   "/spɒnˈteɪ.ni.əs/",   "Ngẫu hứng, tự phát",               "We went on a spontaneous weekend road trip.",                9, True,  True,  False, False, False),
            ("cherish",       "/ˈtʃer.ɪʃ/",         "Trân trọng, nâng niu",             "Always cherish small happy moments with family.",            8, True,  True,  False, False, False),
            ("glow-up",       "/ˈɡloʊ.ʌp/",         "Lột xác tích cực (ngoại hình/tư duy)", "Consistent habits gave her a huge glow-up this year.",   5, True,  False, False, False, False),
            ("overwhelmed",   "/ˌoʊ.vərˈwelmd/",    "Quá tải, choáng ngợp",             "Take a short break whenever you feel overwhelmed.",          4, True,  False, False, False, False),
            ("procrastinate", "/prəˈkræs.tɪ.neɪt/", "Trì hoãn công việc",               "Breaking tasks into tiny steps helps me stop procrastinating.", 3, True, False, False, False, False),
            ("cozy",          "/ˈkoʊ.zi/",          "Ấm cúng, dễ chịu",                 "A rainy evening with hot tea feels so cozy.",                2, False, False, False, False, False),
            ("refreshing",    "/rɪˈfreʃ.ɪŋ/",       "Tươi mát, sảng khoái, mới mẻ",     "Her honest perspective was really refreshing.",              2, False, False, False, False, False),
            ("genuine",       "/ˈdʒen.ju.ɪn/",      "Chân thành, thật lòng",            "A genuine smile brightens everyone's mood.",                 1, False, False, False, False, False),
            ("consistent",    "/kənˈsɪs.tənt/",     "Kiên trì, đều đặn, nhất quán",     "Small consistent efforts beat rare intense bursts.",         1, False, False, False, False, False),
            ("accomplish",    "/əˈkʌm.plɪʃ/",       "Hoàn thành, đạt được mục tiêu",    "Write down three things you want to accomplish today.",      0, False, False, False, False, False),
        ),
    ),

    # =========================================================================
    # #97 — HACHIWARE SKY STUDY (IELTS / TOEIC ACADEMIC VOCAB)
    # =========================================================================
    VocabThemeDef(
        num=97,
        stem="97_Hachiware_IELTS_Academic_Vocab",
        short_key="97_hachiware_ielts_vocab",
        slug="hachiware_ielts_vocab",
        char_name="Hachiware",
        title_en="HACHIWARE SKY STUDY • IELTS ACADEMIC",
        subtitle_vi="Sổ từ vựng Học thuật IELTS / TOEIC chuyên sâu kèm Band, Collocation & Word Family",
        emoji="📘",
        mode="ielts",
        primary="#4A82B8",
        primary_dark="#2B4C7E",
        soft="#CFE8FF",
        page="#F5FAFF",
        card="#FFFFFF",
        ink="#1F3654",
        muted="#5B7699",
        line="#BBD9F7",
        on_primary="#FFFFFF",
        accent_alt="#7CB2E6",
        warn_fill="#E0F2FE",
        warn_ink="#0369A1",
        font_display="Cambria",
        font_caps="Constantia",
        font_vn="Segoe UI",
        font_num="Constantia",
        stage_names=("Bỡ ngỡ đầu", "Sẵn sàng ôn", "Ghi chú kỹ", "Tiến bộ nhanh", "Cổ vũ hết mình", "Band 8.5 100%"),
        practice_steps=(
            "📘 Chọn 1 chủ đề thi trọng tâm (Education / Environment / Tech / Work)",
            "🔗 Học thuộc cả cụm Collocation ăn điểm thay vì học từ đơn lẻ",
            "🔄 Đối chiếu từ đồng nghĩa (Synonyms) để paraphrase mượt Writing Task 2",
            "🙈 Bật 'Ẩn Nghĩa' để tự kiểm tra nghĩa học thuật của 10 từ Band C1–C2",
            "✍️ Tự đặt 2 câu luận ngắn áp dụng từ vừa học & tick hoàn thành!",
        ),
        guide_method_title="📘  PHƯƠNG PHÁP HỌC TỪ VỰNG IELTS BAND 7.0–8.5",
        guide_method_bullets=(
            "1. Phân loại rõ từng từ theo Band/Level (B1–C2) và 6 Chủ đề thi phổ biến nhất (Education, Environment, Technology, Work, Society, Health).",
            "2. Luôn ghi cụm Collocation tự nhiên (vd: 'mitigate climate risks', 'foster innovation') — đây là tiêu chí ăn điểm Lexical Resource của giám khảo IELTS.",
            "3. Theo dõi biểu đồ phân bố chủ đề tại tab 📊 Thống Kê để bổ sung ngay những chủ đề còn mỏng từ trước ngày thi!",
        ),
        toast_perfect="📘 Hachiware tự hào quá! Kho từ học thuật IELTS của bạn đã bứt phá ngoạn mục! ✨",
        toast_practice="🎓 Tuyệt đỉnh! Hoàn tất trọn bộ 5 bước luyện IELTS cùng Hachiware!",
        # (word, ipa, band, topic, meaning, collocation, synonyms, example, status, mastered)
        samples=(
            ("mitigate",      "/ˈmɪt.ɪ.ɡeɪt/",      "C2 (8.0+)", "Environment", "Giảm nhẹ, làm dịu hậu quả",       "mitigate climate risks",        "alleviate, ease, curb",         "Governments must act swiftly to mitigate environmental damage.", "Đã thuộc", True),
            ("foster",        "/ˈfɒs.tər/",         "C1 (7.0+)", "Education",   "Thúc đẩy, nuôi dưỡng phát triển", "foster critical thinking",      "cultivate, nurture, promote",   "Schools should foster creativity alongside academic rigor.",     "Đã thuộc", True),
            ("ubiquitous",    "/juːˈbɪk.wɪ.təs/",   "C2 (8.0+)", "Technology",  "Phổ biến khắp mọi nơi",           "become ubiquitous in daily life","omnipresent, pervasive",       "Smartphones have become ubiquitous in modern classrooms.",       "Đã thuộc", True),
            ("lucrative",     "/ˈluː.krə.tɪv/",     "C1 (7.0+)", "Work",        "Sinh lời cao, béo bở",            "a lucrative career path",       "profitable, rewarding",         "Data analytics has emerged as a highly lucrative profession.",   "Đã thuộc", True),
            ("alleviate",     "/əˈliː.vi.eɪt/",     "C1 (7.0+)", "Society",     "Làm giảm bớt (nghèo đói/áp lực)", "alleviate urban poverty",       "relieve, lessen, mitigate",     "Targeted subsidies can alleviate financial strain on families.", "Đã thuộc", True),
            ("detrimental",   "/ˌdet.rɪˈmen.təl/",  "C1 (7.0+)", "Health",      "Gây hại, bất lợi nghiêm trọng",   "have a detrimental effect on",  "harmful, damaging, adverse",    "Sedentary lifestyles are detrimental to long-term health.",      "Đang ôn",  False),
            ("curriculum",    "/kəˈrɪk.jə.ləm/",    "B2",        "Education",   "Chương trình giảng dạy",          "revamp the school curriculum",  "syllabus, course framework",    "Coding should be integrated into the primary curriculum.",       "Đang ôn",  False),
            ("sustainable",   "/səˈsteɪ.nə.bəl/",   "B2",        "Environment", "Bền vững, thân thiện môi trường", "sustainable urban development", "eco-friendly, viable, green",   "Investing in solar power promotes sustainable growth.",          "Đang ôn",  False),
            ("automation",    "/ˌɔː.təˈmeɪ.ʃən/",   "C1 (7.0+)", "Technology",  "Sự tự động hóa",                  "workplace automation wave",     "mechanization, digitization",   "Rapid automation is reshaping traditional manufacturing jobs.",  "Đang ôn",  False),
            ("disparity",     "/dɪˈspær.ə.ti/",     "C2 (8.0+)", "Society",     "Sự chênh lệch, bất bình đẳng",    "widen the income disparity",    "gap, inequality, imbalance",    "Remote access may help narrow the educational disparity.",       "Đang ôn",  False),
            ("burnout",       "/ˈbɜːn.aʊt/",        "B2",        "Work",        "Kiệt sức vì áp lực công việc",    "prevent employee burnout",      "exhaustion, fatigue",           "Flexible schedules significantly reduce workplace burnout.",     "Đang ôn",  False),
            ("unprecedented", "/ʌnˈpres.ɪ.den.tɪd/","C1 (7.0+)", "Society",     "Chưa từng có tiền lệ",            "at an unprecedented pace",      "unmatched, extraordinary",      "AI tools are evolving at an unprecedented global scale.",        "Mới học",  False),
            ("feasible",      "/ˈfiː.zə.bəl/",      "C1 (7.0+)", "Work",        "Khả thi, có thể thực hiện được",  "an economically feasible plan", "viable, practical, workable",   "Expanding public rail is a feasible solution to congestion.",    "Mới học",  False),
            ("sedentary",     "/ˈsed.ən.tər.i/",    "C2 (8.0+)", "Health",      "Ít vận động, ngồi nhiều",         "lead a sedentary lifestyle",    "inactive, desk-bound",          "Office workers often struggle with a sedentary routine.",        "Mới học",  False),
            ("obsolete",      "/ˌɒb.səlˈiːt/",      "C1 (7.0+)", "Technology",  "Lỗi thời, không còn sử dụng",     "render old skills obsolete",    "outdated, archaic, defunct",    "Lifelong learning ensures workers never become obsolete.",       "Mới học",  False),
        ),
    ),

    # =========================================================================
    # #98 — USAGI HONEY FLASHCARD (2-WAY QUIZ + SPEAKING PHRASAL/IDIOMS)
    # =========================================================================
    VocabThemeDef(
        num=98,
        stem="98_Usagi_Flashcard_Quiz_Speaking",
        short_key="98_usagi_flashcard_vocab",
        slug="usagi_flashcard_vocab",
        char_name="Usagi",
        title_en="USAGI HONEY FLASHCARD • SPEAKING QUIZ",
        subtitle_vi="Thẻ Flashcard Dò bài 2 chiều (Ẩn Nghĩa / Ẩn Từ) cho Phrasal Verbs & Idioms giao tiếp",
        emoji="🍯",
        mode="flashcard",
        primary="#D98236",
        primary_dark="#6E472B",
        soft="#FFF0B8",
        page="#FFFDF5",
        card="#FFFFFF",
        ink="#5A3921",
        muted="#8F6A49",
        line="#F6D59B",
        on_primary="#FFFFFF",
        accent_alt="#FFB085",
        warn_fill="#FEF3C7",
        warn_ink="#B45309",
        font_display="Segoe Print",
        font_caps="Book Antiqua",
        font_vn="Segoe UI",
        font_num="Book Antiqua",
        stage_names=("Nằm nghỉ nạp", "Mở thẻ ôn", "Luyện nói mic", "Nhảy hào hứng", "Cổ vũ Speaking", "Siêu sao 100%"),
        practice_steps=(
            "🙈 Bật công tắc 'Ẩn Nghĩa' (B11) để dò nhanh 10 thẻ từ Anh → Việt",
            "🔄 Đảo chiều: tắt B11, bật 'Ẩn Từ' (E11) để phản xạ ngược Việt → Anh!",
            "🎤 Đọc to câu hội thoại áp dụng với ngữ điệu tự nhiên như người bản xứ",
            "⭐ Cập nhật số sao tự tin (1–5 sao) sau khi tự nói lại không nhìn thẻ",
            "🍯 Bấm nút 'Dò Bài Ngẫu Nhiên' (bản Pro) hoặc tự thưởng 1 món ngon!",
        ),
        guide_method_title="🍯  CHẾ ĐỘ FLASHCARD DÒ BÀI 2 CHIỀU KHÔNG CẦN MACRO",
        guide_method_bullets=(
            "1. Công tắc B11 (🙈 Ẩn Nghĩa): che toàn bộ cột Nghĩa để bạn nhìn Phrasal Verb/Idiom và đoán nghĩa nhanh (chạy mượt cả Excel lẫn Google Sheets!).",
            "2. Công tắc E11 (🙈 Ẩn Từ): che cột Từ vựng & Phát âm để luyện phản xạ dịch ngược Việt → Anh cực hiệu quả cho Speaking!",
            "3. Chấm điểm độ tự tin từ ⭐ đến ⭐⭐⭐⭐⭐ và tick 'Đã dùng khi nói' để biến từ thụ động thành phản xạ tự nhiên.",
        ),
        toast_perfect="🍯 Yaha! Usagi nhảy múa ăn mừng — Phản xạ Speaking của bạn lên trình 100%! ✨",
        toast_practice="🎤 Đỉnh quá! Hoàn thành xong 5 bước luyện Speaking Flashcard cùng Usagi!",
        # (expr, pron, kind, meaning, dialogue, confidence, used_speaking)
        samples=(
            ("break the ice",         "/breɪk ði aɪs/",        "Idiom",        "Phá vỡ bầu không khí ngại ngùng",    "Let's play a quick game to break the ice!",                   "⭐⭐⭐⭐⭐", True),
            ("call it a day",         "/kɔːl ɪt ə deɪ/",       "Idiom",        "Nghỉ tay, kết thúc ngày làm việc",   "We've finished all slides—let's call it a day!",              "⭐⭐⭐⭐⭐", True),
            ("on the same page",      "/ɒn ðə seɪm peɪdʒ/",    "Idiom",        "Cùng chung suy nghĩ, đồng thuận",    "Quick sync to make sure we're all on the same page.",         "⭐⭐⭐⭐⭐", True),
            ("hit the nail on the head","/hɪt ðə neɪl.../",    "Idiom",        "Nói trúng phóc trọng tâm",           "You really hit the nail on the head with that idea!",         "⭐⭐⭐⭐",   True),
            ("pull through",          "/pʊl θruː/",            "Phrasal Verb", "Vượt qua giai đoạn khó khăn",        "It was a tough week, but our team pulled through!",           "⭐⭐⭐⭐",   True),
            ("figure out",            "/ˈfɪɡ.ər aʊt/",         "Phrasal Verb", "Tìm ra lời giải, hiểu ra vấn đề",    "Don't worry, we'll figure out a smarter way together.",       "⭐⭐⭐⭐",   False),
            ("catch up with",         "/kætʃ ʌp wɪð/",         "Phrasal Verb", "Gặp gỡ hỏi thăm / theo kịp tiến độ", "Let's grab matcha this Sunday and catch up!",                 "⭐⭐⭐",     False),
            ("burn the midnight oil", "/bɜːn ðə ˈmɪd.naɪt/",   "Idiom",        "Thức khuya cày bài / làm việc",      "No need to burn the midnight oil if you plan early.",         "⭐⭐⭐",     False),
            ("come across",           "/kʌm əˈkrɒs/",          "Phrasal Verb", "Tình cờ bắt gặp / tạo ấn tượng",     "I came across such a cute bakery near the station.",          "⭐⭐⭐",     False),
            ("piece of cake",         "/piːs əv keɪk/",        "Idiom",        "Dễ như ăn bánh",                     "After practicing daily, that speaking part was a piece of cake!", "⭐⭐⭐", False),
            ("look forward to",       "/lʊk ˈfɔː.wəd tuː/",    "Phrasal Verb", "Háo hức mong chờ điều gì",           "I'm really looking forward to our winter holiday!",           "⭐⭐",       False),
            ("out of the blue",       "/aʊt əv ðə bluː/",      "Idiom",        "Bất thình lình, không báo trước",    "She texted me out of the blue with great news!",              "⭐⭐",       False),
            ("give it a shot",        "/ɡɪv ɪt ə ʃɒt/",        "Idiom",        "Thử làm xem sao, cứ mạnh dạn thử",   "Even if it seems tricky, just give it a shot!",               "⭐⭐",       False),
            ("get the hang of",       "/ɡet ðə hæŋ əv/",       "Idiom",        "Nắm bắt được nhịp, làm quen tay",    "Give it three days and you'll get the hang of it.",           "⭐",         False),
            ("silver lining",         "/ˈsɪl.vər ˈlaɪ.nɪŋ/",   "Idiom",        "Tia hy vọng trong khó khăn",         "Every setback has a silver lining if you stay positive.",     "⭐",         False),
        ),
    ),

    # =========================================================================
    # #99 — MOMONGA LAVENDER MEDIA (MULTI-LANGUAGE MOVIES/SONGS/BOOKS)
    # =========================================================================
    VocabThemeDef(
        num=99,
        stem="99_Momonga_MultiLang_Media_Vocab",
        short_key="99_momonga_media_vocab",
        slug="momonga_media_vocab",
        char_name="Momonga",
        title_en="MOMONGA LAVENDER • MEDIA VOCAB",
        subtitle_vi="Sưu tầm từ vựng Đa Ngôn Ngữ (Anh / Trung / Nhật / Hàn) qua Phim, Nhạc, Podcast & Truyện",
        emoji="💜",
        mode="media",
        primary="#8C62B8",
        primary_dark="#4A3566",
        soft="#E5D4FF",
        page="#FAF7FF",
        card="#FFFFFF",
        ink="#3E2A57",
        muted="#7C6896",
        line="#D6BFF7",
        on_primary="#FFFFFF",
        accent_alt="#FCE1F2",
        warn_fill="#FCE7F3",
        warn_ink="#9D174D",
        font_display="Gabriola",
        font_caps="Palatino Linotype",
        font_vn="Segoe UI",
        font_num="Palatino Linotype",
        stage_names=("Mơ màng ngủ", "Đọc sách say", "Chill kem ngon", "Tỏa sáng tự tin", "Sưu tầm quà", "Bay bổng 100%"),
        practice_steps=(
            "🎬 Xem 15 phút phim / nghe 1 bài hát ngoại ngữ yêu thích & bắt lấy 3 cụm từ hay",
            "📝 Ghi lại Phiên âm / Pinyin / Furigana / Romaji + đúng câu thoại trích dẫn",
            "🎭 Phân loại sắc thái (Thân mật / Trang trọng / Slang / Lãng mạn) để dùng đúng ngữ cảnh",
            "🙈 Bật 'Ẩn Nghĩa' ôn lại bộ sưu tập từ từ phim/nhạc của tuần này",
            "💜 Nhại lại 2 câu thoại tâm đắc nhất (Shadowing) để Momonga cổ vũ bạn!",
        ),
        guide_method_title="💜  HỌC ĐA NGÔN NGỮ QUA SỞ THÍCH (ANH • TRUNG • NHẬT • HÀN)",
        guide_method_bullets=(
            "1. Chọn ngôn ngữ đang học tại ô Dropdown B8 (🇬🇧 Anh / 🇨🇳 Trung / 🇯🇵 Nhật / 🇰🇷 Hàn). Cột D linh hoạt điền IPA, Pinyin, Furigana hay Romaji đều đẹp!",
            "2. Lưu kèm Nguồn trích dẫn (tên bộ phim, bài hát, podcast, cuốn truyện) và Sắc thái để nhớ ngữ cảnh tự nhiên cực lâu.",
            "3. Bộ đếm Media tự tổng hợp bạn đã thu hoạch bao nhiêu từ từ Phim, Bài hát, Podcast và Sách tại tab 📊 Thống Kê!",
        ),
        toast_perfect="💜 Momonga khen siêu đỉnh! Bộ sưu tập từ vựng Phim & Nhạc hôm nay trọn vẹn 100%! ✨",
        toast_practice="🎬 Xuất sắc! Bạn đã hoàn thành trọn vẹn 5 bước học ngoại ngữ qua Media!",
        # (expr, pron_multi, meaning, source_title, media_type, nuance, quote, mastered, status)
        samples=(
            ("bittersweet",        "/ˌbɪt.əˈswiːt/",         "Vừa ngọt ngào vừa man mác buồn",     "La La Land (Movie)",        "Phim",        "Lãng mạn",   "The ending was so bittersweet yet unforgettable.",      True,  "Đã thuộc"),
            ("wanderlust",         "/ˈwɒn.də.lʌst/",         "Niềm khao khát đi du lịch khám phá", "The Secret Life of Walter", "Phim",        "Lãng mạn",   "Her travel vlog sparked instant wanderlust in me.",     True,  "Đã thuộc"),
            ("vibe check",         "/vaɪb tʃek/",            "Cảm nhận bầu không khí / năng lượng","TikTok / Pop Culture",      "Podcast",     "Slang / GenZ","This pastel cafe totally passed the vibe check!",       True,  "Đã thuộc"),
            ("head over heels",    "/hed ˈoʊ.vər hiːlz/",    "Yêu say đắm, mê mệt",                "Taylor Swift Lyrics",       "Bài hát",     "Lãng mạn",   "She fell head over heels for the cozy seaside town.",   True,  "Đã thuộc"),
            ("no-brainer",         "/ˌnoʊˈbreɪ.nər/",        "Quyết định quá hiển nhiên, dễ chọn", "Daily English Podcast",     "Podcast",     "Thân mật",   "Joining the study club was an absolute no-brainer.",    True,  "Đã thuộc"),
            ("plot twist",         "/plɒt twɪst/",           "Cú ngoặt bất ngờ trong cốt truyện",  "K-Drama / Mystery Series",  "Phim",        "Thân mật",   "Nobody saw that final episode plot twist coming!",      False, "Đang ôn"),
            ("nostalgic",          "/nɒsˈtæl.dʒɪk/",         "Hoài niệm, nhớ về kỷ niệm xưa",      "Studio Ghibli OST",         "Bài hát",     "Lãng mạn",   "That piano melody makes me feel deeply nostalgic.",     False, "Đang ôn"),
            ("low-key",            "/ˌloʊˈkiː/",             "Nhẹ nhàng, kín đáo, hơi hơi",        "Chill Lo-Fi Podcast",       "Podcast",     "Slang / GenZ","I low-key love studying on rainy Sunday mornings.",     False, "Đang ôn"),
            ("binge-watch",        "/ˈbɪndʒ.wɒtʃ/",          "Cày phim liền tù tì nhiều tập",      "Netflix Chill Night",       "Phim",        "Thân mật",   "We binge-watched the entire Chiikawa season!",          False, "Đang ôn"),
            ("ephemeral",          "/ɪˈfem.ər.əl/",          "Phù du, đẹp nhưng chóng tàn",        "Japanese Novel (Trans.)",   "Sách/Truyện", "Trang trọng","Cherry blossoms remind us how ephemeral spring is.",    False, "Đang ôn"),
            ("heartwarming",       "/ˈhɑːrt.wɔːr.mɪŋ/",      "Ấm lòng, cảm động dễ thương",        "Slice of Life Anime",       "Phim",        "Thân mật",   "Such a heartwarming story about true friendship.",      False, "Đang ôn"),
            ("resonate with",      "/ˈrez.ə.neɪt wɪð/",      "Chạm tới cảm xúc, đồng cảm sâu sắc", "Book Club Podcast",         "Podcast",     "Trang trọng","The chorus really resonates with young dreamers.",      False, "Mới học"),
            ("daydream",           "/ˈdeɪ.driːm/",           "Mơ mộng giữa ban ngày",              "Indie Acoustic Song",       "Bài hát",     "Lãng mạn",   "She gazed out the train window lost in a daydream.",    False, "Mới học"),
            ("page-turner",        "/ˈpeɪdʒˌtɜː.nər/",       "Cuốn sách hấp dẫn không đặt xuống được","Goodreads Bestseller",    "Sách/Truyện", "Thân mật",   "I stayed up late because that novel is a page-turner.", False, "Mới học"),
            ("komorebi (木漏れ日)", "/ko-mo-re-bi/ (JP mẫu)", "Ánh nắng xuyên qua kẽ lá (mẫu đổi Nhật/Trung/Hàn)", "Japanese Essay", "Sách/Truyện", "Lãng mạn",   "Ghi chú: đổi sang Trung (Pinyin) / Hàn (Romaji) tương tự!", False, "Mới học"),
        ),
    ),

    # =========================================================================
    # #100 — SHISA MATCHA BOOKSHOP (EXAM SPRINT & MISTAKE BANK)
    # =========================================================================
    VocabThemeDef(
        num=100,
        stem="100_Chiikawa_Exam_Sprint_MistakeBank",
        short_key="100_shisa_exam_vocab",
        slug="shisa_exam_vocab",
        char_name="Shisa",
        title_en="SHISA MATCHA BOOKSHOP • EXAM SPRINT",
        subtitle_vi="Nước rút ôn thi với Đếm ngược ngày thi & Ngân hàng 'Từ Hay Quên / Cặp Từ Dễ Nhầm'",
        emoji="🍵",
        mode="exam",
        primary="#4C8C5A",
        primary_dark="#2E5E3A",
        soft="#D8EED9",
        page="#FCF8F0",
        card="#FFFFFF",
        ink="#2B4230",
        muted="#637D68",
        line="#BFE0C2",
        on_primary="#FFFFFF",
        accent_alt="#FAD2CC",
        warn_fill="#FEE2E2",
        warn_ink="#B91C1C",
        font_display="Georgia",
        font_caps="Palatino Linotype",
        font_vn="Segoe UI",
        font_num="Georgia",
        stage_names=("Ngó bài chút", "Ngồi nghiêm túc", "Chăm chép bài", "Mắt sáng hiểu", "Hào hứng ôn", "Đỗ đạt 100%!"),
        practice_steps=(
            "⏳ Kiểm tra số ngày Đếm ngược tới kỳ thi & đặt mục tiêu cứu gấp 5 từ báo đỏ",
            "🚨 Mở bảng 'Từ hay quên cần cứu gấp' (Số lần quên ≥ 2) ở bên dưới để xử lý dứt điểm",
            "🧠 Đọc to Mẹo nhớ nhanh (Mnemonic) để phân biệt rạch ròi từng cặp từ bẫy thi",
            "🙈 Bật 'Ẩn Nghĩa' và tự phân biệt cặp từ dễ nhầm — nếu còn nhầm, tăng 'Số lần quên' +1",
            "🍵 Khi đã phân biệt chuẩn 100%, tick 'Đã hết nhầm' để Shisa cổ vũ bạn đỗ đạt!",
        ),
        guide_method_title="🍵  CHIẾN THUẬT NƯỚC RÚT & NGÂN HÀNG 'TỪ HAY QUÊN'",
        guide_method_bullets=(
            "1. Nhập Ngày Thi thực tế vào ô F6 (tab 📚 Kho Từ Vựng) — đồng hồ 'Đếm ngược ngày thi' sẽ tự tính chính xác số ngày còn lại bằng hàm TODAY().",
            "2. Bất kỳ từ nào bạn hay quên (cột H Số lần quên ≥ 2) và chưa tick 'Đã hết nhầm' sẽ lập tức báo đỏ '🚨 CỨU GẤP!' và tự động gom vào danh sách cứu gấp ở tab 🎯 Luyện Tập!",
            "3. Ghi ngắn gọn Mẹo nhớ nhanh (Mnemonic) cho mỗi cặp từ dễ nhầm (vd: 'stationEry = Envelope = văn phòng phẩm') để không bao giờ sập bẫy phòng thi!",
        ),
        toast_perfect="🍵 Shisa chúc mừng! Bạn đã quét sạch bẫy thi & sẵn sàng đỗ đạt 100%! ✨",
        toast_practice="🏆 Xuất sắc! Hoàn thành 5 bước ôn thi nước rút cực cháy cùng Shisa!",
        # (word, ipa, confusing_pair, meaning_diff, mnemonic, mistake_count, mastered, example)
        samples=(
            ("affect",      "/əˈfekt/",         "vs. effect (danh từ: kết quả)",     "Động từ: tác động, ảnh hưởng đến",        "A = Action (động từ) • E = End result (kết quả)",      0, True,  "Lack of sleep can seriously affect your concentration."),
            ("compliment",  "/ˈkɒm.plɪ.mənt/",  "vs. complement (bổ sung hoàn thiện)","Lời khen ngợi chân thành",                "complIment = I like you (khen) • complEment = Enhance",0, True,  "She received a warm compliment on her presentation."),
            ("stationery",  "/ˈsteɪ.ʃən.ər.i/", "vs. stationary (đứng yên cố định)", "Văn phòng phẩm (bút, sổ, giấy)",          "stationEry = Envelope (giấy bút) • stationAry = At rest", 1, True,  "Matcha bookshop sells adorable pastel stationery."),
            ("principal",   "/ˈprɪn.sə.pəl/",   "vs. principle (nguyên tắc đạo đức)","Hiệu trưởng / Chính, quan trọng nhất",    "princiPAL = your PAL (người hiệu trưởng)",              1, True,  "The school principal congratulated all top scorers."),
            ("emigrate",    "/ˈem.ɪ.ɡreɪt/",    "vs. immigrate (nhập cư vào nước)",  "Di cư rời khỏi đất nước (Exit)",          "Emigrate = Exit (đi ra) • Immigrate = In (đi vào)",     0, True,  "Her grandparents emigrated from Europe in 1960."),
            ("desert",      "/ˈdez.ət/",        "vs. dessert (món tráng miệng)",     "Sa mạc khô cằn (1 chữ s)",                "deSSert có 2 chữ S = Sweet & Strawberry (tráng miệng)", 3, False, "Cacti thrive even in harsh desert climates."),
            ("loose",       "/luːs/",           "vs. lose (đánh mất, thua cuộc)",    "Rộng thùng thình, lỏng lẻo (2 chữ o)",    "lOOse rộng nên dư 2 chữ O • lose mất mất 1 chữ O!",    3, False, "Tie your shoelaces tightly so they don't come loose."),
            ("advice",      "/ədˈvaɪs/",        "vs. advise (động từ: khuyên bảo)",  "Danh từ không đếm được: lời khuyên",      "adviCe = danh từ (như Ice) • adviSe = động từ",         2, False, "Thank you for your thoughtful exam advice!"),
            ("farther",     "/ˈfɑː.ðər/",       "vs. further (sâu hơn, thêm nữa)",   "Xa hơn về khoảng cách vật lý",            "FARther chứa chữ FAR (khoảng cách địa lý)",             2, False, "The library is farther from my house than the park."),
            ("breath",      "/breθ/",           "vs. breathe (động từ: hít thở)",    "Danh từ: hơi thở (không có chữ e cuối)",  "breathe thêm 'e' để kéo dài hơi thở (động từ)",         2, False, "Take a deep breath before opening the exam paper."),
            ("elicit",      "/ɪˈlɪs.ɪt/",       "vs. illicit (bất hợp pháp)",        "Gợi ra, khơi gợi câu trả lời",            "il-licit = illegal (trái luật) • elicit = evoke",       3, False, "Her question elicited a lively class discussion."),
            ("discreet",    "/dɪˈskriːt/",      "vs. discrete (rời rạc, tách biệt)", "Thận trọng, kín đáo, tế nhị",             "discrE-tE tách 2 chữ E bởi T = tách biệt (discrete)",   2, False, "Please be discreet when sharing sensitive feedback."),
            ("allusion",    "/əˈluː.ʒən/",      "vs. illusion (ảo giác, ảo tưởng)",  "Sự ám chỉ gián tiếp (văn học)",           "Allusion = Reference • Illusion = Magic trick",         1, False, "The essay makes a subtle allusion to Shakespeare."),
            ("ensure",      "/ɪnˈʃʊər/",        "vs. insure (mua bảo hiểm)",         "Đảm bảo chắc chắn điều gì xảy ra",        "Insure = Insurance (bảo hiểm) • Ensure = Make sure",    1, False, "Double-check formulas to ensure 100% accuracy."),
            ("historic",    "/hɪˈstɒr.ɪk/",     "vs. historical (thuộc lịch sử)",    "Mang tính lịch sử trọng đại (bước ngoặt)","historic = important moment • historical = old/past",   1, False, "Reaching 100 templates is a historic milestone!"),
        ),
    ),
]
