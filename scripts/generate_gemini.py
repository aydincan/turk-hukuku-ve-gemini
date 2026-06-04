#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini ve Türk Hukuku — depo üreteci.

Aynı `scripts/catalog.json` + `scripts/content.json` (paylaşılan kaynak) üzerinden
Google **Gemini CLI extension** formatını üretir:

  gemini-extension.json                 -> kök: extension manifesti (name, version, contextFileName)
  GEMINI.md                             -> kök: metodoloji + kaynak hijyeni (her oturumda yüklü)
  skills/<alan>/SKILL.md                -> alan başına bir skill (özet + yönlendirme)
  skills/<alan>/references/*.md          -> o alanın ~12 alt-konusu (denetim şemaları)
  README.md, SKILLS.md

Galeri için: public repo + `gemini-cli-extension` GitHub topic'i + kökte gemini-extension.json.
Gemini oturum başında skill'lerin name+description'larını okur, eşleşince `activate_skill`
ile tam içeriği yükler.
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "scripts", "catalog.json")
CONTENT = os.path.join(ROOT, "scripts", "content.json")
SKILLS_DIR = os.path.join(ROOT, "skills")
CONTEXT_FILE = "GEMINI.md"

cat = json.load(open(CATALOG, encoding="utf-8"))
content = json.load(open(CONTENT, encoding="utf-8"))
_p = cat["pazar"]
gruplar = cat["gruplar"]
eklentiler = cat["eklentiler"]

PAZAR = {
    "baslik": "Gemini ve Türk Hukuku",
    "sahip": _p["sahip"],
    "lisans": _p["lisans"],
    "ithaf": _p["ithaf"],
    "homepage": "https://github.com/aydincan/gemini-ve-turk-hukuku",
    "kurulum_yolu": "aydincan/gemini-ve-turk-hukuku",
    "aciklama": ("Gemini ve Türk Hukuku — Google Gemini CLI için Türk hukuku Agent Skills "
                 "koleksiyonu. Her hukuk alanı bir skill; metodoloji, atıf hijyeni, sözleşme, "
                 "dava ve mütalaa iş akışları. Katı kaynak hijyeni: içtihat yalnızca "
                 "mahkeme + daire + esas/karar no + tarih + doğrulanabilir kaynakla; "
                 "uydurma karar numarası yok."),
}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def skill_aciklama(e):
    kw = ", ".join(e.get("anahtar", [])[:8])
    return (f"{e['aciklama']} Bu beceriyi {e['baslik']} alanındaki sorular, olaylar ve "
            f"belgeler için kullan ({kw}). Alan dışı konularda tetiklenme.").replace('"', "'")


def build_skill_md(e, beceriler, referans_var):
    slug = e["slug"]
    kanunlar = ", ".join(e.get("kanunlar", [])) or "ilgili mevzuat"
    konu_satir = "\n".join(
        f"| {b['ad']} | [`references/{b['slug']}.md`](references/{b['slug']}.md) | {b['aciklama']} |"
        for b in beceriler
    )
    metod = ("\n- Alanın metodolojisi ve kaynak notu: "
             "[`references/_metodoloji.md`](references/_metodoloji.md)") if referans_var else ""
    return f"""---
name: {slug}
description: "{skill_aciklama(e)}"
---

# {e['baslik']}

{e['aciklama']}

**Başat mevzuat:** {kanunlar}

## Çalışma akışı

1. **Süre/aciliyet taraması:** Hak düşürücü süre, zamanaşımı, tebligat, duruşma, itiraz
   süresi var mı? Varsa önce onu sabitle.
2. **Olayı sabitle:** Çekişmesiz/çekişmeli olgular ve eksikler; en çok bir gezelim soru.
3. **Alt-konuya in:** Aşağıdaki tablodan ilgili konuyu seç ve `references/<konu>.md`
   dosyasını oku; oradaki denetim şemasını uygula.
4. **Altlama ve sonuç:** Olay → norm → altlama → gerekçeli sonuç; somut sonraki adım.

## Alt-konular

| Konu | Referans | Ne zaman? |
|---|---|---|{("\n" + konu_satir) if konu_satir else ""}{metod}

## Kaynak kuralı (özet)

İçtihat yalnızca doğrulanmış künyeyle (mahkeme + daire + esas/karar no + tarih +
doğrulanabilir kaynak); **model hafızasından karar numarası üretme**; emin olunmayan künye
`[doğrulanacak]`. Mevzuat madde/fıkra ile. `turk-hukuku-mevzuat-mcp` /
`turk-hukuku-ictihat-mcp` araçları kuruluysa metni hafızadan değil onlardan çek
(`madde_getir`, `ictihat_ara`, `karar_getir`). Ayrıntılı kural kökteki `{CONTEXT_FILE}`'dedir.

---

*Deneysel; hukuki danışmanlık değildir. Çıktılar yürürlükteki mevzuat ve doğrulanmış
içtihatla teyit edilmelidir. Bkz. `SORUMLULUK-REDDI.md`.*
"""


def build_reference(b):
    return f"{b['govde_md'].strip()}\n"


def build_metodoloji_ref(e, referans_md):
    return f"{referans_md.strip()}\n"


def build_context_md():
    return f"""# GEMINI.md — Gemini ve Türk Hukuku

Bu depo, **Google Gemini CLI için Türk hukuku Agent Skills** koleksiyonudur; bir Gemini CLI
**extension** olarak paketlenmiştir. `skills/` altında her hukuk alanı bir skill'dir; alanın
alt-konuları o skill'in `references/` klasöründedir. Gemini CLI oturum
başında skill'lerin name+description'larını okur; bir görev bir skill'in tanımıyla eşleşince
`activate_skill` ile tam içeriği yükler. Bu dosya (GEMINI.md) **her oturumda yüklü** kalır ve
aşağıdaki yöntem ile **kaynak hijyeni** kurallarını tüm skill'ler için bağlar.

## Kim için

Avukat, hukuk müşaviri, hâkim/savcı adayı, akademisyen ve hukuk öğrencisi. Türk hukukunun
kendi sistematiğine göre (özel/kamu hukuku, suç genel teorisi, dava şartları) düzenlenmiştir.

## Çalışma yöntemi (her görevde)

1. **Önce süre/aciliyet:** Hak düşürücü süre, zamanaşımı, tebligat, itiraz/dava süresi.
2. **Olayı sabitle:** Çekişmesiz/çekişmeli olgular, eksikler. Gerekiyorsa tek somut soru.
3. **Doğru alana yönel:** İlgili `skills/<alan>` skill'ini ve uygun
   `references/<konu>.md` dosyasını kullan.
4. **Altlama (subsumption):** Olay → norm → şartların somut olaya uygulanması → ara sonuç.
5. **Gerekçeli sonuç:** Risk haritası ve somut sonraki adım; sorumlu kişi ve süre.

## Kaynak hijyeni (DEĞİŞMEZ — tüm skill'ler için)

- **İçtihat asla model hafızasından zikredilmez.** Her karar; mahkeme (Yargıtay / Danıştay /
  Anayasa Mahkemesi / BAM / BİM), daire, **esas ve karar numarası**, tarih ve doğrulanabilir
  kaynak ile verilir (`karararama.yargitay.gov.tr`, `karararama.danistay.gov.tr`,
  `kararlarbilgibankasi.anayasa.gov.tr`, `mevzuat.gov.tr`, UYAP Emsal).
  **Esas/karar numarası ÜRETME.** Emin olunmayan künye `[doğrulanacak]` işaretlenir.
- **Mevzuat** madde/fıkra/bent ile gösterilir (ör. "TBK m.49/1", "HMK m.114/1-ç").
- **Doktrin** yalnızca kullanıcı kaynağı veya lisanslı erişimle; yazar-eser-baskı-sayfa ile.
- Varsayımlar açıkça "varsayım" diye işaretlenir; sahte kesinlik üretilmez.
- MCP araçları varsa resmî metni onlardan çek. `turk-hukuku-mevzuat-mcp` kuruluysa
  kanun/madde metnini hafızadan değil `madde_getir` / `kanun_metni_getir` / `mevzuat_ara`
  ile getir; `turk-hukuku-ictihat-mcp` kuruluysa kararları `ictihat_ara` / `karar_getir`
  ile bulup künyeyi (mahkeme, esas/karar no, tarih) aynen aktar. Bu araçlar mevcutsa
  doğrulamada önce onları kullan; yoksa yukarıdaki künye kuralları aynen geçerlidir.

## Sınırlar

Bu skill'ler avukatlık/hukuki danışmanlık yerine geçmez; nihai sorumluluk yetkili
hukukçudadır. Belgelerle/net beyanla desteklenmeyen vakıalar olgu gibi değerlendirilmez.
Ayrıntı: `SORUMLULUK-REDDI.md`.

## İthaf

{PAZAR['ithaf']}
"""


def build_readme(skill_count, topic_count):
    kurulum = PAZAR["kurulum_yolu"]
    bloklar = []
    for gk, gad in gruplar.items():
        ge = [e for e in eklentiler if e["grup"] == gk]
        if not ge:
            continue
        satir = "\n".join(f"| `{e['slug']}` | {e['baslik']} | {e['aciklama']} |" for e in ge)
        bloklar.append(f"### {gad}\n\n| Skill | Başlık | Açıklama |\n|---|---|---|\n{satir}\n")
    katalog = "\n".join(bloklar)
    return f"""# {PAZAR['baslik']}

> **{PAZAR['baslik']}** — Google **Gemini CLI** için Türk hukuku **Agent Skills** koleksiyonu.
> Her hukuk alanı bir skill; metodoloji, atıf hijyeni, sözleşme, dava ve mütalaa iş akışları.

{PAZAR['aciklama']}

**{skill_count} skill · {topic_count} alt-konu (references) · {PAZAR['lisans']}**

**Yazar:** {PAZAR['sahip']}

> *{PAZAR['ithaf']}*

---

## ⚠️ Önce bunu okuyun

Bu proje **hukuki danışmanlık değildir** ve denenmiş bir ürün değil; teknik bir oyun
alanıdır. Çıktılar **yürürlükteki mevzuat ve doğrulanmış güncel içtihatla** teyit
edilmelidir. Ayrıntı: [`SORUMLULUK-REDDI.md`](./SORUMLULUK-REDDI.md).

## Kurulum (Google Gemini CLI)

Bu depo bir **Gemini CLI extension**'ıdır (`gemini-extension.json` + `skills/` + `GEMINI.md`).

**Doğrudan kur (önerilen):**

```bash
gemini extensions install https://github.com/{kurulum}
```

**Galeriden (adres yazmadan):** Extension, Gemini CLI **Extensions Gallery**'sinde otomatik
indekslenir; Gemini içinde `/extensions` ile göz atıp adını seçerek kurabilirsiniz.

Kurulduktan sonra `skills/` altındaki alan-skill'leri ve kök `GEMINI.md` otomatik yüklenir;
göreviniz bir skill'in tanımıyla eşleşince Gemini onu `activate_skill` ile devreye alır.

## Nasıl çalışır?

1. Gemini CLI oturum başında tüm skill'lerin **name + description**'larını okur.
2. Kökteki [`GEMINI.md`](./GEMINI.md) her oturumda yüklenir — yöntem + **kaynak hijyeni**.
3. Olayınızı anlatın; göreviniz bir skill'in tanımıyla eşleşince Gemini `activate_skill` ile
   o alanı yükler (ya da `/skills` ile listeleyip elle seçin).
4. Skill sizi alt-konuya (`references/<konu>.md`) yönlendirir; denetim şeması uygulanır.

## Kaynak hijyeni (omurga)

İçtihat asla model hafızasından zikredilmez; her karar mahkeme + daire + **esas/karar no** +
tarih + doğrulanabilir kaynakla verilir; emin olunmayan künye `[doğrulanacak]`. (Bkz. `GEMINI.md`.)

## Skill kataloğu

{katalog}

## Lisans

**{PAZAR['lisans']}** — [`LICENSE-APACHE`](./LICENSE-APACHE), [`LICENSE-MIT`](./LICENSE-MIT),
[`NOTICE`](./NOTICE).

> "Gemini" ve "Google" Google'ın markalarıdır; bu proje Google ile resmî olarak ilişkili değildir.
"""


def build_skills_index(topic_map):
    lines = ["# Skill Dizini (SKILLS.md)\n",
             "Her alan bir skill'dir; alt-konular o skill'in `references/` klasöründedir.\n"]
    for gk, gad in gruplar.items():
        ge = [e for e in eklentiler if e["grup"] == gk]
        if not ge:
            continue
        lines.append(f"\n## {gad}\n")
        for e in ge:
            lines.append(f"\n### `{e['slug']}` — {e['baslik']}\n")
            for b in topic_map[e["slug"]]:
                lines.append(f"- `references/{b['slug']}.md` — {b['ad']}")
    return "\n".join(lines) + "\n"


def build_extension_json():
    obj = {
        "name": "turk-hukuku-skills",
        "version": "1.0.0",
        "description": ("Türk hukuku için Agent Skills — 81 hukuk alanı, 1000+ alt-konu; "
                        "metodoloji, atıf hijyeni, dava ve mütalaa. Hukuki danışmanlık değildir."),
        "contextFileName": "GEMINI.md",
    }
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main():
    shutil.rmtree(SKILLS_DIR, ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT, ".agents"), ignore_errors=True)  # eski düzen temizliği
    skill_count = 0
    topic_count = 0
    topic_map = {}
    for e in eklentiler:
        slug = e["slug"]
        c = content.get(slug, {}) or {}
        beceriler = c.get("beceriler") or []
        topic_map[slug] = beceriler
        base = os.path.join(SKILLS_DIR, slug)
        referans_md = c.get("referans_md", "")
        write(os.path.join(base, "SKILL.md"),
              build_skill_md(e, beceriler, bool(referans_md)))
        if referans_md:
            write(os.path.join(base, "references", "_metodoloji.md"),
                  build_metodoloji_ref(e, referans_md))
        for b in beceriler:
            write(os.path.join(base, "references", f"{b['slug']}.md"), build_reference(b))
            topic_count += 1
        skill_count += 1

    write(os.path.join(ROOT, CONTEXT_FILE), build_context_md())
    write(os.path.join(ROOT, "README.md"), build_readme(skill_count, topic_count))
    write(os.path.join(ROOT, "SKILLS.md"), build_skills_index(topic_map))
    write(os.path.join(ROOT, "gemini-extension.json"), build_extension_json())
    print(f"Üretildi: {skill_count} skill, {topic_count} alt-konu (references) + gemini-extension.json.")


if __name__ == "__main__":
    main()
