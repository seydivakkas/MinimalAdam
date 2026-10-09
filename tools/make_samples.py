#!/usr/bin/env python3
"""P1: Özgün, yazısız 16:9 MinimalAdam sahneleri üretir. Yazıyı bu dosya ÜRETMEZ.

SVG'deki karakter sembolü aynı kalır, kompozisyon ve eylemi değişir.
"""
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / 'examples' / 'specs'
GENERATED = ROOT / 'examples' / 'generated'
OUTPUT_EXAMPLES = ROOT / 'minimaladam' / 'assets' / 'examples'

HEADER = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
width="1600" height="900" viewBox="0 0 1600 900">
<rect width="1600" height="900" fill="white"/>
<defs>
<g id="minimaladam">
  <!-- Tekrar kullanılabilir gövde silueti; karakter kimliği her sahnede aynı -->
  <path d="M-48 -70 Q-53 -118 -20 -131 Q10 -147 38 -120 Q62 -97 48 -54 Q38 -12 1 -8 Q-39 -12 -48 -70Z" fill="#171717"/>
  <ellipse cx="-17" cy="-91" rx="6.7" ry="8.2" fill="white"/>
  <ellipse cx="17" cy="-92" rx="6.5" ry="8" fill="white"/>
  <path d="M-15 -10 Q-18 3 -25 18 M16 -10 Q19 7 29 18" stroke="#171717" fill="none" stroke-width="6" stroke-linecap="round"/>
</g>
</defs>
'''
FOOTER = '</svg>\n'

# Elle çizilmiş hissi: simetrik olmayan bezier hatları, sınırlı renkler, dokusuz beyaz.
SCENE_1 = '''
<!-- Ana bilgi hattı: parçalar -> süzgeç -> tek derli toplu bilgi -->
<g stroke="#171717" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" fill="none">
<path d="M354 393 l22 -28 l21 17 l-15 21 z M455 485 l27 -12 l16 22 l-24 14 z"/>
<path d="M425 325 l20 -11 l8 21 l-18 9 z M338 508 l28 10 l-9 22 l-21 -8 z"/>
<path d="M550 400 C622 414 667 406 706 428 M564 484 Q635 488 706 476" stroke="#ed8832" stroke-width="6"/>
<path d="M689 419 l18 10 l-21 11 M692 466 l17 8 l-18 13" stroke="#ed8832" stroke-width="6"/>
<!-- Kara delik hissi vermeyen hafif düzensiz süzgeç -->
<path d="M700 357 Q800 347 903 363 L845 489 Q821 518 821 553 L786 553 Q787 518 762 489 Z"/>
<path d="M719 385 Q791 398 881 382" stroke-width="3"/>
<path d="M763 491 Q810 505 848 487" stroke-width="3"/>
<path d="M801 555 Q803 594 865 600 Q915 610 962 601" stroke="#ed8832" stroke-width="6"/>
<path d="M946 591 l18 10 l-18 14" stroke="#ed8832" stroke-width="6"/>
<path d="M1008 597 l19 -22 l22 19 l-16 24 Z"/>
<path d="M1084 577 l23 4 l3 24 l-27 -2 Z"/>
<path d="M1156 587 l15 -16 l18 19 l-16 17 Z"/>
<!-- Çöp sepeti, tek kırmızı vurgu -->
<path d="M648 627 l92 -3 l-12 86 l-66 -3 Z M636 622 l112 0 M672 643 l9 44 M712 643 l-8 44" stroke="#d74b3c" stroke-width="4"/>
<path d="M687 568 Q686 590 695 621" stroke="#d74b3c" stroke-dasharray="7 12" stroke-width="4"/>
</g>
<!-- MinimalAdam süzgecin tahliye kolunu bizzat çekiyor -->
<g transform="translate(848 693) scale(0.94)"><use xlink:href="#minimaladam"/></g>
<path d="M887 622 Q917 592 913 564 L934 553" stroke="#171717" fill="none" stroke-width="6" stroke-linecap="round"/>
<path d="M928 545 q17 -9 22 3 q-1 13 -16 15" stroke="#171717" fill="white" stroke-width="4"/>
<path d="M821 627 Q800 614 788 603" stroke="#171717" fill="none" stroke-width="6" stroke-linecap="round"/>
<path d="M1004 638 Q1120 656 1192 644" stroke="#171717" fill="none" stroke-width="3" stroke-linecap="round" opacity=".45"/>
'''
SCENE_2 = '''
<!-- İki akış platformu ortada kopuyor; MinimalAdam asıl bağlantıyı örüyor -->
<g stroke="#171717" fill="none" stroke-linejoin="round" stroke-linecap="round">
<path d="M334 438 Q465 430 642 440 L650 536 Q520 532 334 541 Z" stroke-width="5"/>
<path d="M949 438 Q1109 430 1276 439 L1270 540 Q1135 546 943 535 Z" stroke-width="5"/>
<path d="M357 480 C465 467 543 467 603 475" stroke="#ed8832" stroke-width="7"/>
<path d="M585 463 l22 12 l-23 16" stroke="#ed8832" stroke-width="6"/>
<path d="M973 475 Q1083 466 1209 482" stroke="#ed8832" stroke-width="7"/>
<path d="M1192 466 l23 17 l-23 12" stroke="#ed8832" stroke-width="6"/>
<path d="M653 430 l-20 22 m29 -7 l-28 28 m18 40 l-19 21" stroke="#d74b3c" stroke-width="4"/>
<path d="M957 432 l-20 24 m24 -4 l-24 26 m18 38 l-20 23" stroke="#d74b3c" stroke-width="4"/>
<!-- Tamir edilen akış, kırık noktadan geçirilmiş ip -->
<path d="M624 480 C702 449 719 510 793 469 C849 431 885 503 966 478" stroke="#ed8832" stroke-width="7"/>
<path d="M737 492 Q759 518 790 529" stroke="#171717" stroke-width="4"/>
<path d="M849 473 Q855 518 894 537" stroke="#171717" stroke-width="4"/>
<path d="M648 540 Q800 558 952 541" stroke="#3a79ad" stroke-width="3" stroke-dasharray="10 19"/>
</g>
<!-- Ellerinden ip geçen MinimalAdam, orta noktada görevi yerine getiriyor -->
<g transform="translate(806 687) scale(1)"><use xlink:href="#minimaladam"/></g>
<path d="M759 619 Q728 579 742 499 M848 616 Q895 566 886 508" fill="none" stroke="#171717" stroke-width="6" stroke-linecap="round"/>
<circle cx="742" cy="499" r="10" fill="white" stroke="#171717" stroke-width="4"/>
<circle cx="886" cy="508" r="10" fill="white" stroke="#171717" stroke-width="4"/>
<path d="M707 687 q95 16 190 -1" fill="none" stroke="#171717" stroke-width="3" opacity=".45"/>
'''
SCENE_3 = '''
<!-- Karar tartısı: belirsiz varsayıma karşı somut kanıt -->
<g stroke="#171717" fill="none" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
<path d="M798 358 C797 453 800 548 799 670" stroke-width="7"/>
<path d="M743 677 Q798 643 857 675 Q861 688 849 693 L751 693 Q734 687 743 677Z"/>
<path d="M541 421 Q795 401 1058 372" stroke-width="8"/>
<circle cx="802" cy="394" r="22" fill="white" stroke-width="6"/>
<path d="M570 419 Q574 481 542 560 M700 413 Q705 477 726 556" stroke-width="4"/>
<path d="M894 386 Q895 466 874 533 M1030 376 Q1037 452 1050 533" stroke-width="4"/>
<path d="M517 562 Q635 588 749 552 Q735 621 624 627 Q528 625 517 562Z"/>
<path d="M850 532 Q964 557 1077 528 Q1070 599 972 605 Q872 605 850 532Z"/>
<path d="M574 535 l43 -47 l40 34 l-45 48Z" stroke="#d74b3c" stroke-width="4" stroke-dasharray="12 9"/>
<path d="M629 542 l36 -27 l22 29" stroke="#d74b3c" stroke-width="4"/>
<!-- Kanıt blokları (çok az) -->
<path d="M917 526 l35 -38 l44 29 l-37 40 z M959 515 l44 -40 l38 40 l-43 38 z"/>
<path d="M912 508 l10 6 m68 -25 l16 13" stroke="#3a79ad" stroke-width="4"/>
<path d="M1057 382 Q1122 376 1163 358" stroke="#ed8832" stroke-width="5"/>
<path d="M1148 345 l18 12 l-16 17" stroke="#ed8832" stroke-width="5"/>
</g>
<!-- MinimalAdam kanıt kutusunu bizzat kefeye koyuyor -->
<g transform="translate(1132 671) scale(.91)"><use xlink:href="#minimaladam"/></g>
<path d="M1086 597 Q1053 566 1044 538" stroke="#171717" fill="none" stroke-width="6" stroke-linecap="round"/>
<path d="M1098 596 Q1073 560 1085 525" stroke="#171717" fill="none" stroke-width="6" stroke-linecap="round"/>
<path d="M1012 493 l33 -26 l27 35 l-35 26Z" fill="white" stroke="#171717" stroke-width="5" stroke-linejoin="round"/>
<path d="M1003 696 q100 10 181 0" fill="none" stroke="#171717" stroke-width="3" opacity=".45"/>
'''

SCENES = [
    ('01-bilgiyi-suz', SCENE_1, [
        dict(text='Dağınık bilgi',x=.275,y=.305,color='black',size=40),
        dict(text='Süzgeç',x=.50,y=.305,color='blue',size=40),
        dict(text='Net fikir',x=.70,y=.305,color='black',size=40),
        dict(text='Gereksiz',x=.428,y=.83,color='red',size=35),
    ]),
    ('02-kopan-baglantiyi-onar', SCENE_2, [
        dict(text='Girdi',x=.31,y=.365,color='black',size=40),
        dict(text='Kopukluk',x=.5,y=.32,color='red',size=40),
        dict(text='Çıktı',x=.69,y=.365,color='black',size=40),
        dict(text='Onarım',x=.50,y=.82,color='blue',size=35),
    ]),
    ('03-kanitla-karar-ver', SCENE_3, [
        dict(text='Varsayım',x=.37,y=.33,color='red',size=40),
        dict(text='Kanıt',x=.62,y=.305,color='blue',size=40),
        dict(text='Karar',x=.79,y=.33,color='black',size=40),
    ]),
]


def main():
    from render_turkish_labels import render
    for folder in (SPECS, GENERATED, OUTPUT_EXAMPLES):
        folder.mkdir(parents=True, exist_ok=True)
    for name, elements, labels in SCENES:
        svg_path = SPECS / (name + '.base.svg')
        base_path = GENERATED / (name + '.base.png')
        spec_path = SPECS / (name + '.labels.json')
        svg_path.write_text(HEADER + elements + FOOTER, encoding='utf-8')
        spec_path.write_text(json.dumps({'version':1,'labels':labels},ensure_ascii=False,indent=2) + '\n',encoding='utf-8')
        try:
            import cairosvg  # yalnızca P1 özgün SVG sahne kaynağı yeniden inşa edilirse
            cairosvg.svg2png(url=str(svg_path), write_to=str(base_path), output_width=1600, output_height=900)
        except (ImportError, OSError) as err:
            raise RuntimeError('P1 kaynak SVG sahnelerinin yeniden rasterleştirilmesi için '
                               'isteğe bağlı CairoSVG + yerel Cairo DLL gerekir. '
                               'Yayın betiği, P3 üretimi ve mevcut P1 örnekleri bunu gerektirmez.') from err
        result = render(base_path,spec_path,GENERATED/(name+'.png'))
        (OUTPUT_EXAMPLES/(name+'.png')).write_bytes(result['image'].read_bytes())
        print(f"PASS {name}: {len(labels)} etiket, temel SVG ve tam PNG")

if __name__ == '__main__':
    main()
