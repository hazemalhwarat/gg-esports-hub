# GG Esports Hub

مجمّع منافسات الايسبورتس عبر كل الألعاب في مكان واحد: بثوث Twitch/YouTube الحيّة،
نتائج ومباريات، وبطولات قادمة — مع تمييز الفرق العربية وتنبيهات Discord.
كل المصادر مجانية.

## المكوّنات

```
gg-esports-hub/
├── collector/        # مجمّع البيانات (Python) — يشتغل على GitHub Actions
│   ├── sources/      # مصدر لكل مزوّد: twitch, youtube, startgg, opendota
│   ├── config.py     # الفرق ذات الأولوية + قوائم القنوات + المستويات
│   ├── run.py        # المشغّل الرئيسي
│   └── ...
├── dashboard/        # واجهة Next.js — تقرأ dashboard/public/data.json
└── .github/workflows/collect.yml   # الجدولة المتدرّجة
```

كيف يشتغل: المجمّع يجمع من المصادر كل بضع دقائق، يكتب `dashboard/public/data.json`،
ويرفعه للريبو. Vercel يخدم الداشبورد، والداشبورد يقرأ الملف ويحدّث نفسه كل دقيقة.

## المفاتيح المطلوبة (كلها مجانية)

انسخ `.env.example` إلى `.env` واملأ ما تقدر عليه. أي مفتاح ناقص = المصدر يُتجاهل
بهدوء دون تعطيل الباقي.

| المتغير | من وين | لماذا |
|---|---|---|
| `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` | dev.twitch.tv/console/apps | البثوث الحيّة + المشاهدين |
| `YOUTUBE_API_KEY` | console.cloud.google.com (YouTube Data API v3) | بثوث YouTube الحيّة |
| `STARTGG_TOKEN` | start.gg/admin/profile/developer | البطولات القادمة |
| `DISCORD_WEBHOOK_URL` | Discord: Integrations > Webhooks | التنبيهات |

OpenDota لا يحتاج مفتاح.

## التشغيل محلياً

المجمّع:
```bash
pip install -r requirements.txt
cd collector
python run.py --tier full     # أو --tier live
```

الداشبورد:
```bash
cd dashboard
npm install
npm run dev        # http://localhost:3000
```

الداشبورد يعرض بيانات تجريبية جاهزة حتى قبل أول تشغيل للمجمّع.

## النشر

- **الداشبورد:** اربط الريبو بـ Vercel، الجذر = مجلد `dashboard`.
- **المجمّع:** يشتغل تلقائياً على GitHub Actions. أضف المفاتيح في
  Settings > Secrets and variables > Actions. المستوى `live` كل 3 دقائق
  (بثوث + Dota)، والمستوى `full` كل 15 دقيقة (كل شي).

## المصادر المفعّلة الآن (11 مصدر)

**بثوث:** Twitch، YouTube، Kick.
**مباريات (APIs):** OpenDota (Dota 2)، vlrggapi (Valorant)، lolesports (LoL)،
Octane.gg (Rocket League)، Aligulac (StarCraft II).
**مباريات (سكرابينغ):** HLTV (CS2, أفضل جهد).
**العمود الفقري الموحّد:** Liquipedia يغطي 17 لعبة (CS2، Dota، Valorant، LoL،
Rocket League، R6، Overwatch، Mobile Legends، Honor of Kings، PUBG Mobile،
Free Fire، Call of Duty، Apex، Fortnite، StarCraft II، Clash Royale، Brawl Stars).
**بطولات:** start.gg.

الخريطة الكاملة لكل مصدر (مفعّل ومخطّط) في **SOURCES.md**.

## المفاتيح الإضافية الاختيارية

`ALIGULAC_KEY` لمصدر StarCraft II (مفتاح مجاني من aligulac.com/about/api).
باقي المصادر الجديدة (VLR، LoL، Octane، Kick، HLTV، Liquipedia) لا تحتاج مفاتيح.

## توسيع القوائم

- الفرق ذات الأولوية: `collector/config.py` → `PRIORITY_ORGS`
- قنوات Twitch / YouTube / Kick: `TWITCH_CHANNELS` / `YOUTUBE_CHANNELS` / `KICK_CHANNELS`
- ألعاب Liquipedia: `LIQUIPEDIA_WIKIS` (أضف اسم الويكي، تُغطّى اللعبة كاملة بلا كود)

## ملاحظة عن المصادر بالسكرابينغ

HLTV و Liquipedia يعتمدان على تحليل HTML وقد يحتاجان ضبط المُحدّدات بعد أول
تشغيل حي (المواقع تغيّر بنيتها أحياناً). لا يعطّلان النظام لو انكسرا، فقط
يرجعان نتائج فارغة. أرسل لي أي خطأ يظهر وقت التشغيل الفعلي وأضبطه.

## خارطة الطريق

مفصّلة في **SOURCES.md**. باختصار: تصنيفات HLTV/VLR، منصات بث كورية/صينية
(SOOP، Bilibili)، رُوسترات Liquipedia + دمج موديول الانتقالات، Esports Charts
للمشاهدات، وربط شبكة أخبار RSS.
