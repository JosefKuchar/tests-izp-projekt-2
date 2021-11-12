#!/usr/bin/python3
#
# Testy na 2. IZP projekt 2021
# Vytvoril Josef Kuchar (xkucha28) - josefkuchar.com
# Priklad pouziti: ./test.py setcal
# Help se vypise pres argument -h
# Revize: 1

from subprocess import run, PIPE
import sys
import argparse
from typing import Counter, Tuple

OK = "\033[1;32;40m[ OK ]\033[0;37;40m"
FAIL = "\033[1;31;40m[FAIL]\033[0;37;40m"

class Tester:
    def __init__(self, program_name):
        self.program_name = './' + program_name
        self.test_count = 0
        self.pass_count = 0

    def compare_output(self, output, stdout):
        out_list = output.rstrip().split('\n')
        stdout_list = stdout.rstrip().split('\n')

        if len(out_list) != len(stdout_list):
            return False

        for i in range(0, len(out_list)):
            stdout_line = stdout_list[i].split(' ')
            out_line = out_list[i].split(' ')
            if stdout_line[0] == 'R' or stdout_line[0] == 'S':
                if Counter(stdout_line) != Counter(out_line):
                    return False
            elif stdout_list[i] != out_list[i]:
                return False
        return True

    def test(self, test_name, args, output_file="", intentional_error=False):
        self.test_count += 1
        error = False
        msg = ""
        p = None

        try:
            p = run([self.program_name] + args, stdout=PIPE, stderr=PIPE, encoding='ascii')
        except UnicodeDecodeError as e:
            print(FAIL, test_name)
            print('Vystup pravdepodobne obsahuje znaky mimo ASCII (diakritika?)')
            print(e)
            sys.exit()
        except Exception as e:
            print(FAIL, test_name)
            print('Chyba pri volani programu!')
            print(e)
            sys.exit()

        if p.returncode != 0:
            if not intentional_error:
                error = True
                msg += 'Program vratil chybovy navratovy kod ({}) prestoze nemel!\n'.format(p.returncode)
        else:
            if intentional_error:
                error = True
                msg += 'Program vratil uspesne dokonceni (kod 0) prestoze nemel!\n'

        output = ""
        if not intentional_error:
            out_file = open(output_file, "r")
            output = out_file.read()

            if not self.compare_output(output, p.stdout):
                error = True
                msg += 'Vystup programu se neshoduje s predpokladanym vystupem!\n'

            out_file.close()

        if intentional_error and p.stderr == '':
            error = True
            msg += 'Program nevratil na STDERR zadnou chybovou zpravu!\n'

        if error:
            print(FAIL, test_name)
            print(msg)
            print('Argumenty:', ' '.join(args))
            print("Predpokladany vystup:")
            print(output)
            print("STDOUT:")
            print(p.stdout)
            print("STDERR:")
            print(p.stderr)
        else:
            self.pass_count += 1
            print(OK, test_name)

    def print_stats(self):
        print('Uspesnost: {}/{} ({:.2f}%)'.format(self.pass_count, self.test_count, (self.pass_count / self.test_count) * 100))
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tester 1. IZP projektu')
    parser.add_argument('prog', metavar='P', type=str, help='Jmeno programu (napriklad: pwcheck)')
    parser.add_argument('--bonus', dest='bonus', action='store_true', help='Kontrola bonusoveho parsovani argumentu')
    parser.add_argument('--no-color', dest='color', action='store_false', help='Vystup bez barev')
    args = parser.parse_args()

    if not args.color:
        OK = '[ OK ]'
        FAIL = '[FAIL]'

    t1 = Tester(args.prog)
    t2 = Tester(args.prog)

    # Testy ze zadani
    t1.test('Test ze zadani #1 (sets.txt)', ['tests/sets.txt'], 'tests/sets_res.txt')
    t1.test('Test ze zadani #2 (rel.txt)', ['tests/rel.txt'], 'tests/rel_res.txt')

    # Zakladni testovani argumentu
    t1.test('Bez argumentu', [], intentional_error=True)
    t1.test('Moc argumentu', ['tests/sets.txt', 'tests/rel.txt'], intentional_error=True)
    t1.test('Neexistujici soubor', ['tests/a'], intentional_error=True)

    # Testovani validity souboru
    t1.test('Nevalidni soubor #01 Pouze univerzum', ['tests/universe_only.txt'], intentional_error=True)
    t1.test('Nevalidni soubor #02 Spatne poradi definic', ['tests/wrong_order.txt'], intentional_error=True)
    t1.test('Nevalidni soubor #03 Prilis dlouhy nazev prvku', ['tests/too_long.txt'], intentional_error=True)
    t1.test('Nevalidni soubor #04 Prazdny radek', ['tests/empty_line.txt'], intentional_error=True)
    t1.test('Nevadidni soubor #05 Bez mezery po zacatku', ['tests/no_space.txt'], intentional_error=True)
    t1.test('Nevalidni soubor #06 Spatny znak v definici', ['tests/invalid_char.txt'], intentional_error=True)

    # Command empty
    t1.test('Prikaz "empty" #1 Prazdna mnozina', ['tests/empty/0.txt'], 'tests/empty/0_res.txt')
    t1.test('Prikaz "empty" #2 Neprazdna mnozina', ['tests/empty/1.txt'], 'tests/empty/1_res.txt')
    t1.test('Prikaz "empty" #3 Relace', ['tests/empty/2.txt'], intentional_error=True)
    t1.test('Prikaz "empty" #4 Zadny parametr', ['tests/empty/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "empty" #5 Moc parametru', ['tests/empty/too_many.txt'], intentional_error=True)

    # Command card
    t1.test('Prikaz "card" #1 Prazdna mnozina', ['tests/card/0.txt'], 'tests/card/0_res.txt')
    t1.test('Prikaz "card" #2 Mnozina o velikosti 1', ['tests/card/1.txt'], 'tests/card/1_res.txt')
    t1.test('Prikaz "card" #3 Mnozina o velikosti 5', ['tests/card/2.txt'], 'tests/card/2_res.txt')
    t1.test('Prikaz "card" #4 Relace', ['tests/card/3.txt'], intentional_error=True)
    t1.test('Prikaz "card" #5 Zadny parametr', ['tests/card/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "card" #6 Moc parametru', ['tests/card/too_many.txt'], intentional_error=True)

    # Command complement
    t1.test('Prikaz "complement" #1 Prazdne univerzum, prazdna mnozina', ['tests/complement/0.txt'], 'tests/complement/0_res.txt')
    t1.test('Prikaz "complement" #2 Univerzum a mnozina stejne prvky', ['tests/complement/1.txt'], 'tests/complement/1_res.txt')
    t1.test('Prikaz "complement" #3 Univerzum a prazdna mnozina', ['tests/complement/2.txt'], 'tests/complement/2_res.txt')
    t1.test('Prikaz "complement" #4 Univerzum a neprazdna mnozina', ['tests/complement/3.txt'], 'tests/complement/3_res.txt')
    t1.test('Prikaz "complement" #5 Relace', ['tests/complement/4.txt'], intentional_error=True)
    t1.test('Prikaz "complement" #6 Zadny parametr', ['tests/complement/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "complement" #7 Moc parametru', ['tests/complement/too_many.txt'], intentional_error=True)

    # Command union
    t1.test('Prikaz "union" #01 Dve prazdne mnoziny', ['tests/union/0.txt'], 'tests/union/0_res.txt')
    t1.test('Prikaz "union" #02 Prvni prazdna, druha neprazdna', ['tests/union/1.txt'], 'tests/union/1_res.txt')
    t1.test('Prikaz "union" #03 Prvni neprazdna, druha prazdna', ['tests/union/2.txt'], 'tests/union/2_res.txt')
    t1.test('Prikaz "union" #04 Mnoziny bez pruniku', ['tests/union/3.txt'], 'tests/union/3_res.txt')
    t1.test('Prikaz "union" #05 Mnoziny s prunikem', ['tests/union/4.txt'], 'tests/union/4_res.txt')
    t1.test('Prikaz "union" #06 Mnozina sama se sebou', ['tests/union/5.txt'], 'tests/union/5_res.txt')
    t1.test('Prikaz "union" #07 Relace jako prvni parametr', ['tests/union/6.txt'], intentional_error=True)
    t1.test('Prikaz "union" #08 Relace jako druhy parametr', ['tests/union/7.txt'], intentional_error=True)
    t1.test('Prikaz "union" #09 Zadny parametr', ['tests/union/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "union" #10 Jeden parametr', ['tests/union/one_param.txt'], intentional_error=True)
    t1.test('Prikaz "union" #11 Moc parametru', ['tests/union/too_many.txt'], intentional_error=True)

    # Command intersect
    t1.test('Prikaz "intersect" #1 Cela mnozina', ['tests/intersect/1.txt'], 'tests/intersect/1_res.txt');
    t1.test('Prikaz "intersect" #2 Casti mnoziny', ['tests/intersect/2.txt'], 'tests/intersect/2_res.txt');
    t1.test('Prikaz "intersect" #3 Prazdna mnozina 1', ['tests/intersect/3.txt'], 'tests/intersect/3_res.txt');
    t1.test('Prikaz "intersect" #4 Prazdna mnozina 2', ['tests/intersect/4.txt'], 'tests/intersect/4_res.txt');
    t1.test('Prikaz "intersect" #5 Relace', ['tests/intersect/5.txt'], intentional_error=True);
    t1.test('Prikaz "intersect" #6 Zadne parametry', ['tests/intersect/no_param.txt'], intentional_error=True);
    t1.test('Prikaz "intersect" #7 Moc parametru', ['tests/intersect/too_many.txt'], intentional_error=True);
    t1.test('Prikaz "intersect" #8 Malo parametru', ['tests/intersect/too_few.txt'], intentional_error=True);

    # Command minus
    t1.test('Prikaz "minus" #01 Prazdne mnoziny', ['tests/minus/1.txt'], 'tests/minus/1_res.txt')
    t1.test('Prikaz "minus" #02 Prvni prazdna, druha neprazdna', ['tests/minus/2.txt'], 'tests/minus/2_res.txt')
    t1.test('Prikaz "minus" #03 Prvni neprazdna, druha prazdna', ['tests/minus/3.txt'], 'tests/minus/3_res.txt')
    t1.test('Prikaz "minus" #04 Mnozina sama se sebou', ['tests/minus/4.txt'], 'tests/minus/4_res.txt')
    t1.test('Prikaz "minus" #05 Dve mnoziny bez pruniku', ['tests/minus/5.txt'], 'tests/minus/5_res.txt')
    t1.test('Prikaz "minus" #06 Dve mnoziny s prunikem 1', ['tests/minus/6.txt'], 'tests/minus/6_res.txt')
    t1.test('Prikaz "minus" #07 Dve mnoziny s prunikem 2', ['tests/minus/7.txt'], 'tests/minus/7_res.txt')
    t1.test('Prikaz "minus" #08 Relace jako prvni parametr', ['tests/minus/8.txt'], intentional_error=True)
    t1.test('Prikaz "minus" #09 Relace jako druhy parametr', ['tests/minus/9.txt'], intentional_error=True)
    t1.test('Prikaz "minus" #10 Zadny parametr', ['tests/minus/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "minus" #11 Jeden parametr', ['tests/minus/one_param.txt'], intentional_error=True)
    t1.test('Prikaz "minus" #12 Moc parametru', ['tests/minus/too_many.txt'], intentional_error=True)

    # Command subseteq
    t1.test('Prikaz "subseteq" #01 Prazdne mnoziny', ['tests/subseteq/1.txt'], 'tests/subseteq/1_res.txt')
    t1.test('Prikaz "subseteq" #02 Prvni prazdna, druha neprazdna', ['tests/subseteq/2.txt'], 'tests/subseteq/2_res.txt')
    t1.test('Prikaz "subseteq" #03 Prvni neprazdna, druha prazdna', ['tests/subseteq/3.txt'], 'tests/subseteq/3_res.txt')
    t1.test('Prikaz "subseteq" #04 Dve mnoziny bez pruniku', ['tests/subseteq/4.txt'], 'tests/subseteq/4_res.txt')
    t1.test('Prikaz "subseteq" #05 Mnozina sama se sebou', ['tests/subseteq/5.txt'], 'tests/subseteq/5_res.txt')
    t1.test('Prikaz "subseteq" #06 Dve mnoziny s prunikem', ['tests/subseteq/6.txt'], 'tests/subseteq/6_res.txt')
    t1.test('Prikaz "subseteq" #07 Dve identicke mnoziny', ['tests/subseteq/7.txt'], 'tests/subseteq/7_res.txt')
    t1.test('Prikaz "subseteq" #08 Prvni podmnozina druhe', ['tests/subseteq/8.txt'], 'tests/subseteq/8_res.txt')
    t1.test('Prikaz "subseteq" #09 Relace jako prvni parametr', ['tests/subseteq/9.txt'], intentional_error=True)
    t1.test('Prikaz "subseteq" #10 Relace jako druhy parametr', ['tests/subseteq/10.txt'], intentional_error=True)
    t1.test('Prikaz "subseteq" #11 Zadny parametr', ['tests/subseteq/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "subseteq" #12 Jeden parametr', ['tests/subseteq/one_param.txt'], intentional_error=True)
    t1.test('Prikaz "subseteq" #13 Moc parametru', ['tests/subseteq/too_many.txt'], intentional_error=True)

    # Command subseteq
    t1.test('Prikaz "subset" #01 Prazdne mnoziny', ['tests/subset/1.txt'], 'tests/subset/1_res.txt')
    t1.test('Prikaz "subset" #02 Prvni prazdna, druha neprazdna', ['tests/subset/2.txt'], 'tests/subset/2_res.txt')
    t1.test('Prikaz "subset" #03 Prvni neprazdna, druha prazdna', ['tests/subset/3.txt'], 'tests/subset/3_res.txt')
    t1.test('Prikaz "subset" #04 Dve mnoziny bez pruniku', ['tests/subset/4.txt'], 'tests/subset/4_res.txt')
    t1.test('Prikaz "subset" #05 Mnozina sama se sebou', ['tests/subset/5.txt'], 'tests/subset/5_res.txt')
    t1.test('Prikaz "subset" #06 Dve mnoziny s prunikem', ['tests/subset/6.txt'], 'tests/subset/6_res.txt')
    t1.test('Prikaz "subset" #07 Dve identicke mnoziny', ['tests/subset/7.txt'], 'tests/subset/7_res.txt')
    t1.test('Prikaz "subset" #08 Prvni podmnozina druhe', ['tests/subset/8.txt'], 'tests/subset/8_res.txt')
    t1.test('Prikaz "subset" #09 Relace jako prvni parametr', ['tests/subset/9.txt'], intentional_error=True)
    t1.test('Prikaz "subset" #10 Relace jako druhy parametr', ['tests/subset/10.txt'], intentional_error=True)
    t1.test('Prikaz "subset" #11 Zadny parametr', ['tests/subset/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "subset" #12 Jeden parametr', ['tests/subset/one_param.txt'], intentional_error=True)
    t1.test('Prikaz "subset" #13 Moc parametru', ['tests/subset/too_many.txt'], intentional_error=True)

    # Command equals
    t1.test('Prikaz "equals" #01 Prazdne mnoziny', ['tests/equals/1.txt'], 'tests/equals/1_res.txt')
    t1.test('Prikaz "equals" #02 Prvni prazdna, druha neprazdna', ['tests/equals/2.txt'], 'tests/equals/2_res.txt')
    t1.test('Prikaz "equals" #03 Prvni neprazdna, druha prazdna', ['tests/equals/3.txt'], 'tests/equals/3_res.txt')
    t1.test('Prikaz "equals" #04 Dve mnoziny bez pruniku', ['tests/equals/4.txt'], 'tests/equals/4_res.txt')
    t1.test('Prikaz "equals" #05 Mnozina sama se sebou', ['tests/equals/5.txt'], 'tests/equals/5_res.txt')
    t1.test('Prikaz "equals" #06 Dve mnoziny s prunikem', ['tests/equals/6.txt'], 'tests/equals/6_res.txt')
    t1.test('Prikaz "equals" #07 Dve identicke mnoziny', ['tests/equals/7.txt'], 'tests/equals/7_res.txt')
    t1.test('Prikaz "equals" #08 Relace jako prvni parametr', ['tests/equals/8.txt'], intentional_error=True)
    t1.test('Prikaz "equals" #09 Relace jako druhy parametr', ['tests/equals/9.txt'], intentional_error=True)
    t1.test('Prikaz "equals" #10 Zadny parametr', ['tests/equals/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "equals" #11 Jeden parametr', ['tests/equals/one_param.txt'], intentional_error=True)
    t1.test('Prikaz "equals" #12 Moc parametru', ['tests/equals/too_many.txt'], intentional_error=True)

    # Command reflexive
    t1.test('Prikaz "reflexive" #1 Prazdne univerzum, prazdna relace', ['tests/reflexive/1.txt'], 'tests/reflexive/1_res.txt')
    t1.test('Prikaz "reflexive" #2 Prazdna relace', ['tests/reflexive/2.txt'], 'tests/reflexive/2_res.txt')
    t1.test('Prikaz "reflexive" #3 Reflexivni relace 1', ['tests/reflexive/3.txt'], 'tests/reflexive/3_res.txt')
    t1.test('Prikaz "reflexive" #4 Reflexivni relace 2', ['tests/reflexive/4.txt'], 'tests/reflexive/4_res.txt')
    t1.test('Prikaz "reflexive" #5 Nereflexivni relace', ['tests/reflexive/5.txt'], 'tests/reflexive/5_res.txt')
    t1.test('Prikaz "reflexive" #6 Mnozina', ['tests/reflexive/6.txt'], intentional_error=True)
    t1.test('Prikaz "reflexive" #7 Zadny parametr', ['tests/reflexive/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "reflexive" #8 Moc parametru', ['tests/reflexive/too_many.txt'], intentional_error=True)

    # Command symmetric
    t1.test('Prikaz "symmetric" #1 Prazdne univerzum, prazdna relace', ['tests/symmetric/1.txt'], 'tests/symmetric/1_res.txt')
    t1.test('Prikaz "symmetric" #2 Prazdna relace', ['tests/symmetric/2.txt'], 'tests/symmetric/2_res.txt')
    t1.test('Prikaz "symmetric" #3 Symetricka relace 1', ['tests/symmetric/3.txt'], 'tests/symmetric/3_res.txt')
    t1.test('Prikaz "symmetric" #4 Symetricka relace 2', ['tests/symmetric/4.txt'], 'tests/symmetric/4_res.txt')
    t1.test('Prikaz "symmetric" #5 Nesymetricka relace', ['tests/symmetric/5.txt'], 'tests/symmetric/5_res.txt')
    t1.test('Prikaz "symmetric" #6 Mnozina', ['tests/symmetric/6.txt'], intentional_error=True)
    t1.test('Prikaz "symmetric" #7 Zadny parametr', ['tests/symmetric/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "symmetric" #8 Moc parametru', ['tests/symmetric/too_many.txt'], intentional_error=True)

    if args.bonus:
        # Bonusove reseni
        pass

    print('-- STATISTIKA --')
    print('Zakladni reseni:')
    t1.print_stats()

    if args.bonus:
        print('Bonusove reseni')
        t2.print_stats()
