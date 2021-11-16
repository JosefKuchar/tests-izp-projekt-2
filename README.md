# 🧪 Testy na 2. IZP Projekt [VUT, 2021]
⚠️ Testy nejsou hotové, ještě se určitě změní a obsáhnou víc věcí

## Přispěvatelé 👍
- [galloj](https://github.com/galloj)
- [EvilKiwi](https://github.com/EvilKiwi)

## Instalace
Oficiálně je podporovaný pouze běh na Linuxu (WSL), problémy se spouštěním na Windows řešit nebudu.

Jedna z možností je naklonovat repozitář (popř. stáhnout jako ZIP) a normálně spustit (při případném přesouvání je nutné přesunout i složku `tests` s veškerým obsahem!)

Druhá možnost je přidat si tento repozitář jako submodul do vašeho repozitáře:

`git submodule add -b master https://github.com/JosefKuchar/tests-izp-projekt-2 tests`


### Závislosti
- Python3
- Valgrind (není nutný, ale hodí se)

## Použití
`./test.py [cesta k programu]`, alternativně `python3 test.py [cesta k programu]`

Příklad:

`./test.py setcal` nebo `python3 test.py setcal`

Argumenty:

```
usage: test.py [-h] [--bonus] [--valgrind] [--no-color] P

Tester 2. IZP projektu

positional arguments:
  P           Cesta k programu (napriklad: setcal)

optional arguments:
  -h, --help  show this help message and exit
  --bonus     Kontrola bonusoveho reseni
  --valgrind  Kontrola chyb pomoci valgrindu
  --no-color  Vystup bez barev
```
