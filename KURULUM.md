# Kurulum (Google Gemini CLI)

**Gemini ve Türk Hukuku**, Google **Gemini CLI** için bir **extension** olarak paketlenmiş
bir Agent Skills koleksiyonudur:

- Kökte `gemini-extension.json` (extension manifesti) ve `GEMINI.md` (bağlam dosyası),
- `skills/<alan>/SKILL.md` — her hukuk alanı bir skill,
- her alanın alt-konuları o skill'in `references/` klasöründe.

> Önce [`SORUMLULUK-REDDI.md`](./SORUMLULUK-REDDI.md) dosyasını okuyun. İçerik **hukuki
> danışmanlık değildir** ve doğrulanmadan kullanılmamalıdır.

## A) Doğrudan kur (önerilen)

```bash
gemini extensions install https://github.com/aydincan/turk-hukuku-ve-gemini
```

## B) Galeriden — adres yazmadan

Bu extension, Gemini CLI **Extensions Gallery**'sinde otomatik indekslenir (repo
`gemini-cli-extension` topic'iyle etiketlidir). Gemini içinde `/extensions` ile göz atıp
adını seçerek, repo adresi vermeden kurabilirsiniz.

## Kullanım

- Kurulumdan sonra `skills/` altındaki alan-skill'leri ve kök `GEMINI.md` otomatik yüklenir.
- Gemini oturum başında tüm skill'lerin **name + description**'larını okur.
- Görevinizi anlatın; açıklamanız bir skill'in tanımıyla eşleşince Gemini `activate_skill`
  ile o alanın tam içeriğini yükler. `/skills` ile listeleyip elle de seçebilirsiniz.

## Kaldırma / güncelleme

```bash
gemini extensions update turk-hukuku-skills
gemini extensions uninstall turk-hukuku-skills
```

## Depoyu yeniden üretmek / genişletmek

Tüm skill'ler `scripts/catalog.json` (omurga) ve `scripts/content.json` (hukuki gövde)
dosyalarından üretilir:

```bash
python3 scripts/generate_gemini.py
```

- Yeni bir alan eklemek için `scripts/catalog.json` → `eklentiler` dizisine girdi ekleyin.
- Alt-konu gövdeleri `scripts/content.json` içindedir.
- Üretici `skills/`'i ve `gemini-extension.json`'ı sıfırdan yazar (idempotent); üretilen
  dosyaları elle düzenlemeyin.

## Gereksinimler

- Kullanmak için: **Google Gemini CLI**.
- Depoyu yeniden üretmek için: **Python 3** (ek bağımlılık yoktur).
