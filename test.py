#!/usr/bin/python3
#
# Testy na 2. IZP projekt 2021
# Vytvoril Josef Kuchar (xkucha28) - josefkuchar.com
# Priklad pouziti: ./test.py setcal
# Help se vypise pres argument -h
# Revize: 1

import os
from os import error
from subprocess import run, PIPE
import sys
import argparse
from typing import Counter, Tuple

OK = "\033[1;32m[ OK ]\033[0m"
FAIL = "\033[1;31m[FAIL]\033[0m"
WARN = "\033[1;33m[WARN]\033[0m"

VALGRIND_LOG = 'valgrind-log.txt'

def detect_valgrind():
    try:
        run(['valgrind'], stdout=PIPE, stderr=PIPE)
        return True
    except:
        print(WARN, 'Valgrind neni nainstalovan, pro kontrolu memory leaku nainstalujte valgrind')
        return False

class Tester:
    def __init__(self, program_name, valgrind):
        self.program_name = './' + program_name
        self.test_count = 0
        self.pass_count = 0
        self.valgrind = valgrind

    def check_valgrind(self, args):
        try:
            run(['valgrind', '--track-origins=yes', '--leak-check=full','--quiet', '--log-file=' + VALGRIND_LOG] + [self.program_name] + args, stdout=PIPE, stderr=PIPE)
        except Exception as e:
            print(FAIL, 'Chyba pri spousteni valgrindu!')
            print(e)
            return

        try:
            valgrind_log_file = open(VALGRIND_LOG, 'r')
            valgrind_log = valgrind_log_file.read().strip()

            if valgrind_log != '':
                print(WARN, 'Valgrind detekoval memory leak nebo jinou chybu!')
                print(valgrind_log)
        except Exception as e:
            print(FAIL, 'Nepodarilo se otevrit valgrind log!')
            print(e)
            return

    def compare_output(self, output, stdout):
        out_list = output.rstrip().split('\n')
        stdout_list = stdout.rstrip().split('\n')

        if len(out_list) != len(stdout_list):
            return False

        for i in range(0, len(out_list)):
            stdout_line = stdout_list[i].split(' ')
            out_line = out_list[i].split(' ')
            if stdout_line[0] in ['R', 'S', 'U']:
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

        if self.valgrind:
            self.check_valgrind(args)

    def print_stats(self):
        print('Uspesnost: {}/{} ({:.2f}%)'.format(self.pass_count, self.test_count, (self.pass_count / self.test_count) * 100))
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tester 2. IZP projektu')
    parser.add_argument('prog', metavar='P', type=str, help='Cesta k programu (napriklad: setcal)')
    parser.add_argument('--bonus', dest='bonus', action='store_true', help='Kontrola bonusoveho reseni')
    parser.add_argument('--valgrind', dest='valgrind', action='store_true', help='Kontrola chyb pomoci valgrindu')
    parser.add_argument('--no-color', dest='color', action='store_false', help='Vystup bez barev')
    args = parser.parse_args()

    if not args.color:
        OK = '[ OK ]'
        FAIL = '[FAIL]'
        WARN = '[WARN]'

    valgrind = args.valgrind
    if valgrind:
        valgrind = detect_valgrind()

    t1 = Tester(args.prog, valgrind)
    t2 = Tester(args.prog, valgrind)

    # Testy ze zadani
    t1.test('Test ze zadani #1 (sets.txt)', ['tests/assignment/sets.txt'], 'tests/assignment/sets_res.txt')
    t1.test('Test ze zadani #2 (rel.txt)', ['tests/assignment/rel.txt'], 'tests/assignment/rel_res.txt')

    # Zakladni testovani argumentu
    t1.test('Bez argumentu', [], intentional_error=True)
    t1.test('Moc argumentu', ['tests/sets.txt', 'tests/rel.txt'], intentional_error=True)
    t1.test('Neexistujici soubor', ['tests/a'], intentional_error=True)

    # Testovani univerza
    t1.test('Univerzum #01 Cisla ve jmenech prvku', ['tests/universe/1.txt'], intentional_error=True)
    t1.test('Univerzum #02 Specialni znaky ve jmenech prvku', ['tests/universe/2.txt'], intentional_error=True)
    t1.test('Univerzum #03 Maximalni delka jmena prvku', ['tests/universe/3.txt'], 'tests/universe/3_res.txt')
    t1.test('Univerzum #04 Vetsi nez maximalni delka jmena prvku', ['tests/universe/4.txt'], intentional_error=True)
    t1.test('Univerzum #05 Prvek ma nazev prikazu 1', ['tests/universe/5.txt'], intentional_error=True)
    t1.test('Univerzum #06 Prvek ma nazev prikazu 2', ['tests/universe/6.txt'], intentional_error=True)
    t1.test('Univerzum #07 Prvek ma false', ['tests/universe/7.txt'], intentional_error=True)
    t1.test('Univerzum #08 Opakovani prvku 1', ['tests/universe/8.txt'], intentional_error=True)
    t1.test('Univerzum #09 Opakovani prvku 2', ['tests/universe/9.txt'], intentional_error=True)
    t1.test('Univerzum #10 Zadna mezera za U', ['tests/universe/10.txt'], intentional_error=True)

    # Testovani mnozin
    t1.test('Mnozina #1 Prvky, ktere nepatri do univerza', ['tests/set/1.txt'], intentional_error=True)
    t1.test('Mnozina #2 Opakujici se prvek', ['tests/set/2.txt'], intentional_error=True)
    t1.test('Mnozina #3 Delsi prvek nez maximalni delka', ['tests/set/3.txt'], intentional_error=True)
    t1.test('Mnozina #4 Zadna mezera za S', ['tests/set/4.txt'], intentional_error=True)

    # Testovani relaci
    t1.test('Relace #1 Prvky, ktere nepatri do univerza 1', ['tests/relation/1.txt'], intentional_error=True)
    t1.test('Relace #2 Prvky, ktere nepatri do univerza 2', ['tests/relation/2.txt'], intentional_error=True)
    t1.test('Relace #3 Opakujici se prvek', ['tests/relation/3.txt'], intentional_error=True)
    t1.test('Relace #4 Delsi prvek nez maximalni delka', ['tests/relation/4.txt'], intentional_error=True)
    t1.test('Relace #5 Zadna mezera za R', ['tests/relation/5.txt'], intentional_error=True)

    # Testovani prikazu
    t1.test('Prikaz #1 Neexistujici', ['tests/command/1.txt'], intentional_error=True)
    t1.test('Prikaz #2 Zadna mezera za C', ['tests/command/2.txt'], intentional_error=True)

    # Testovani obecne validity souboru
    t1.test('Obecne #1 Pouze univerzum', ['tests/general/universe_only.txt'], intentional_error=True)
    t1.test('Obecne #2 Spatne poradi definic', ['tests/general/wrong_order.txt'], intentional_error=True)
    t1.test('Obecne #3 Prazdny radek', ['tests/general/empty_line.txt'], intentional_error=True)
    t1.test('Obecne #4 Rozlisovani velikosti pismen', ['tests/general/case_sensitivity.txt'], intentional_error=True)
    t1.test('Obecne #5 2x univerzum', ['tests/general/multiple_universe.txt'], intentional_error=True)
    t1.test('Obecne #6 Zadne univerzum', ['tests/general/no_universe.txt'], intentional_error=True)
    t1.test('Obecne #7 Zadna mnozina nebo relace', ['tests/general/no_set.txt'], intentional_error=True)
    t1.test('Obecne #8 Zadny prikaz', ['tests/general/no_command.txt'], intentional_error=True)
    t1.test('Obecne #9 Nevalidni pocatecni pismeno', ['tests/general/invalid_start.txt'], intentional_error=True)

    # Command empty
    t1.test('Prikaz "empty" #1 Prazdna mnozina', ['tests/empty/0.txt'], 'tests/empty/0_res.txt')
    t1.test('Prikaz "empty" #2 Neprazdna mnozina', ['tests/empty/1.txt'], 'tests/empty/1_res.txt')
    t1.test('Prikaz "empty" #3 Relace', ['tests/empty/2.txt'], intentional_error=True)
    t1.test('Prikaz "empty" #4 Neprazdne univerzum jako mnozina', ['tests/empty/3.txt'], 'tests/empty/3_res.txt')
    t1.test('Prikaz "empty" #5 Prazdne univerzum jako mnozina', ['tests/empty/4.txt'], 'tests/empty/4_res.txt')
    t1.test('Prikaz "empty" #6 Zadny parametr', ['tests/empty/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "empty" #7 Moc parametru', ['tests/empty/too_many.txt'], intentional_error=True)

    # Command card
    t1.test('Prikaz "card" #1 Prazdna mnozina', ['tests/card/0.txt'], 'tests/card/0_res.txt')
    t1.test('Prikaz "card" #2 Mnozina o velikosti 1', ['tests/card/1.txt'], 'tests/card/1_res.txt')
    t1.test('Prikaz "card" #3 Mnozina o velikosti 5', ['tests/card/2.txt'], 'tests/card/2_res.txt')
    t1.test('Prikaz "card" #4 Relace', ['tests/card/3.txt'], intentional_error=True)
    t1.test('Prikaz "card" #5 Neprazdne univerzum jako mnozina', ['tests/card/4.txt'], 'tests/card/4_res.txt')
    t1.test('Prikaz "card" #6 Prazdne univerzum jako mnozina', ['tests/card/5.txt'], 'tests/card/5_res.txt')
    t1.test('Prikaz "card" #7 Zadny parametr', ['tests/card/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "card" #8 Moc parametru', ['tests/card/too_many.txt'], intentional_error=True)

    # Command complement
    t1.test('Prikaz "complement" #1 Prazdne univerzum, prazdna mnozina', ['tests/complement/0.txt'], 'tests/complement/0_res.txt')
    t1.test('Prikaz "complement" #2 Univerzum a mnozina stejne prvky', ['tests/complement/1.txt'], 'tests/complement/1_res.txt')
    t1.test('Prikaz "complement" #3 Univerzum a prazdna mnozina', ['tests/complement/2.txt'], 'tests/complement/2_res.txt')
    t1.test('Prikaz "complement" #4 Univerzum a neprazdna mnozina', ['tests/complement/3.txt'], 'tests/complement/3_res.txt')
    t1.test('Prikaz "complement" #5 Relace', ['tests/complement/4.txt'], intentional_error=True)
    t1.test('Prikaz "complement" #6 Neprazdne univerzum jako mnozina', ['tests/complement/5.txt'], 'tests/complement/5_res.txt')
    t1.test('Prikaz "complement" #7 Prazdne univerzum jako mnozina', ['tests/complement/6.txt'], 'tests/complement/6_res.txt')
    t1.test('Prikaz "complement" #8 Zadny parametr', ['tests/complement/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "complement" #9 Moc parametru', ['tests/complement/too_many.txt'], intentional_error=True)

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
    t1.test('Prikaz "reflexive" #7 Univerzum', ['tests/reflexive/7.txt'], intentional_error=True)
    t1.test('Prikaz "reflexive" #8 Zadny parametr', ['tests/reflexive/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "reflexive" #9 Moc parametru', ['tests/reflexive/too_many.txt'], intentional_error=True)

    # Command symmetric
    t1.test('Prikaz "symmetric" #1 Prazdne univerzum, prazdna relace', ['tests/symmetric/1.txt'], 'tests/symmetric/1_res.txt')
    t1.test('Prikaz "symmetric" #2 Prazdna relace', ['tests/symmetric/2.txt'], 'tests/symmetric/2_res.txt')
    t1.test('Prikaz "symmetric" #3 Symetricka relace 1', ['tests/symmetric/3.txt'], 'tests/symmetric/3_res.txt')
    t1.test('Prikaz "symmetric" #4 Symetricka relace 2', ['tests/symmetric/4.txt'], 'tests/symmetric/4_res.txt')
    t1.test('Prikaz "symmetric" #5 Nesymetricka relace', ['tests/symmetric/5.txt'], 'tests/symmetric/5_res.txt')
    t1.test('Prikaz "symmetric" #6 Mnozina', ['tests/symmetric/6.txt'], intentional_error=True)
    t1.test('Prikaz "symmetric" #7 Univerzum', ['tests/symmetric/7.txt'], intentional_error=True)
    t1.test('Prikaz "symmetric" #8 Zadny parametr', ['tests/symmetric/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "symmetric" #9 Moc parametru', ['tests/symmetric/too_many.txt'], intentional_error=True)

    # Command antisymmetric
    t1.test('Prikaz "antisymmetric" #1 Prazdne univerzum, prazdna relace', ['tests/antisymmetric/1.txt'], 'tests/antisymmetric/1_res.txt')
    t1.test('Prikaz "antisymmetric" #2 Prazna relace', ['tests/antisymmetric/2.txt'], 'tests/antisymmetric/2_res.txt')
    t1.test('Prikaz "antisymmetric" #3 Antisymetricka relace 1', ['tests/antisymmetric/3.txt'], 'tests/antisymmetric/3_res.txt')
    t1.test('Prikaz "antisymmetric" #4 Antisymetricka relace 2', ['tests/antisymmetric/4.txt'], 'tests/antisymmetric/4_res.txt')
    t1.test('Prikaz "antisymmetric" #5 Neantisymetricka', ['tests/antisymmetric/5.txt'], 'tests/antisymmetric/5_res.txt')
    t1.test('Prikaz "antisymmetric" #6 Mnozina', ['tests/antisymmetric/6.txt'], intentional_error=True)
    t1.test('Prikaz "antisymmetric" #7 Univerzum', ['tests/antisymmetric/7.txt'], intentional_error=True)
    t1.test('Prikaz "antisymmetric" #8 Zadny parametr', ['tests/antisymmetric/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "antisymmetric" #9 Moc parametru', ['tests/antisymmetric/too_many.txt'], intentional_error=True)

    # Command transitive
    t1.test('Prikaz "transitive" #1 Prazdne univerzum, prazdna relace', ['tests/transitive/1.txt'], 'tests/transitive/1_res.txt')
    t1.test('Prikaz "transitive" #2 Prazdna relace', ['tests/transitive/2.txt'], 'tests/transitive/2_res.txt')
    t1.test('Prikaz "transitive" #3 Tranzitivni relace 1', ['tests/transitive/3.txt'], 'tests/transitive/3_res.txt')
    t1.test('Prikaz "transitive" #4 Tranzitivni relace 2', ['tests/transitive/4.txt'], 'tests/transitive/4_res.txt')
    t1.test('Prikaz "transitive" #5 Netranzitivni relace', ['tests/transitive/5.txt'], 'tests/transitive/5_res.txt')
    t1.test('Prikaz "transitive" #6 Mnozina', ['tests/transitive/6.txt'], intentional_error=True)
    t1.test('Prikaz "transitive" #7 Univerzum', ['tests/transitive/7.txt'], intentional_error=True)
    t1.test('Prikaz "transitive" #8 Zadny parametr', ['tests/transitive/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "transitive" #9 Moc parametru', ['tests/transitive/too_many.txt'], intentional_error=True)

    # Command domain
    t1.test('Prikaz "domain" #1 Prazdne univerzum, prazdna relace', ['tests/domain/1.txt'], 'tests/domain/1_res.txt')
    t1.test('Prikaz "domain" #2 Relace 1', ['tests/domain/2.txt'], 'tests/domain/2_res.txt')
    t1.test('Prikaz "domain" #3 Relace 2', ['tests/domain/3.txt'], 'tests/domain/3_res.txt')
    t1.test('Prikaz "domain" #4 Relace 3', ['tests/domain/4.txt'], 'tests/domain/4_res.txt')
    t1.test('Prikaz "domain" #5 Relace 4', ['tests/domain/5.txt'], 'tests/domain/5_res.txt')
    t1.test('Prikaz "domain" #6 Mnozina', ['tests/domain/6.txt'], intentional_error=True)
    t1.test('Prikaz "domain" #7 Univerzum', ['tests/domain/7.txt'], intentional_error=True)
    t1.test('Prikaz "domain" #8 Zadny parametr', ['tests/domain/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "domain" #9 Moc parametru', ['tests/domain/too_many.txt'], intentional_error=True)

    # Command codomain
    t1.test('Prikaz "codomain" #1 Prazdne univerzum, prazdna relace', ['tests/codomain/1.txt'], 'tests/codomain/1_res.txt')
    t1.test('Prikaz "codomain" #2 Relace 1', ['tests/codomain/2.txt'], 'tests/codomain/2_res.txt')
    t1.test('Prikaz "codomain" #3 Relace 2', ['tests/codomain/3.txt'], 'tests/codomain/3_res.txt')
    t1.test('Prikaz "codomain" #4 Relace 3', ['tests/codomain/4.txt'], 'tests/codomain/4_res.txt')
    t1.test('Prikaz "codomain" #5 Relace 4', ['tests/codomain/5.txt'], 'tests/codomain/5_res.txt')
    t1.test('Prikaz "codomain" #6 Mnozina', ['tests/codomain/6.txt'], intentional_error=True)
    t1.test('Prikaz "codomain" #7 Univerzum', ['tests/codomain/7.txt'], intentional_error=True)
    t1.test('Prikaz "codomain" #8 Zadny parametr', ['tests/codomain/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "codomain" #9 Moc parametru', ['tests/codomain/too_many.txt'], intentional_error=True)

    # Command function
    t1.test('Prikaz "function" #1 Prazdne univerzum, prazdna relace', ['tests/function/1.txt'], 'tests/function/1_res.txt')
    t1.test('Prikaz "function" #2 Prazdna relace', ['tests/function/2.txt'], 'tests/function/2_res.txt')
    t1.test('Prikaz "function" #3 Funkce 1', ['tests/function/3.txt'], 'tests/function/3_res.txt')
    t1.test('Prikaz "function" #4 Funkce 2', ['tests/function/4.txt'], 'tests/function/4_res.txt')
    t1.test('Prikaz "function" #5 Neni funkce', ['tests/function/5.txt'], 'tests/function/5_res.txt')
    t1.test('Prikaz "function" #6 Mnozina', ['tests/function/6.txt'], intentional_error=True)
    t1.test('Prikaz "function" #7 Univerzum', ['tests/function/7.txt'], intentional_error=True)
    t1.test('Prikaz "function" #8 Zadny parametr', ['tests/function/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "function" #9 Moc parametru', ['tests/function/too_many.txt'], intentional_error=True)

    if args.bonus:
        # Bonusove reseni
        # Command closure_ref
        t2.test('Prikaz "closure_ref" #1 Prazdne univerzum, prazdna relace', ['tests/closure_ref/1.txt'], 'tests/closure_ref/1_res.txt')
        t2.test('Prikaz "closure_ref" #2 Prazdna relace', ['tests/closure_ref/2.txt'], 'tests/closure_ref/2_res.txt')
        t2.test('Prikaz "closure_ref" #3 Reflexivni relace', ['tests/closure_ref/3.txt'], 'tests/closure_ref/3_res.txt')
        t2.test('Prikaz "closure_ref" #4 Nereflexivni relace', ['tests/closure_ref/4.txt'], 'tests/closure_ref/4_res.txt')
        t2.test('Prikaz "closure_ref" #5 Mnozina', ['tests/closure_ref/5.txt'], intentional_error=True)
        t2.test('Prikaz "closure_ref" #6 Univerzum', ['tests/closure_ref/6.txt'], intentional_error=True)
        t2.test('Prikaz "closure_ref" #7 Zadny parametr', ['tests/closure_ref/no_param.txt'], intentional_error=True)
        t2.test('Prikaz "closure_ref" #8 Moc parametru', ['tests/closure_ref/too_many.txt'], intentional_error=True)

        # Command closure_sym
        t2.test('Prikaz "closure_sym" #1 Prazdne univerzum, prazdna relace', ['tests/closure_sym/1.txt'], 'tests/closure_sym/1_res.txt')
        t2.test('Prikaz "closure_sym" #2 Prazdna relace', ['tests/closure_sym/2.txt'], 'tests/closure_sym/2_res.txt')
        t2.test('Prikaz "closure_sym" #3 Symetricka relace', ['tests/closure_sym/3.txt'], 'tests/closure_sym/3_res.txt')
        t2.test('Prikaz "closure_sym" #4 Nesymetricka relace', ['tests/closure_sym/4.txt'], 'tests/closure_sym/4_res.txt')
        t2.test('Prikaz "closure_sym" #5 Mnozina', ['tests/closure_sym/5.txt'], intentional_error=True)
        t2.test('Prikaz "closure_sym" #6 Univerzum', ['tests/closure_sym/6.txt'], intentional_error=True)
        t2.test('Prikaz "closure_sym" #7 Zadny parametr', ['tests/closure_sym/no_param.txt'], intentional_error=True)
        t2.test('Prikaz "closure_sym" #8 Moc parametru', ['tests/closure_sym/too_many.txt'], intentional_error=True)

        # Command closure_trans
        t2.test('Prikaz "closure_trans" #1 Prazdne univerzum, prazdna relace', ['tests/closure_trans/1.txt'], 'tests/closure_trans/1_res.txt')
        t2.test('Prikaz "closure_trans" #2 Prazdna relace', ['tests/closure_trans/2.txt'], 'tests/closure_trans/2_res.txt')
        t2.test('Prikaz "closure_trans" #3 Tranzitivni relace 1', ['tests/closure_trans/3.txt'], 'tests/closure_trans/3_res.txt')
        t2.test('Prikaz "closure_trans" #4 Tranzitivni relace 2', ['tests/closure_trans/4.txt'], 'tests/closure_trans/4_res.txt')
        t2.test('Prikaz "closure_trans" #5 Netranzitivni relace, nekolik iteraci', ['tests/closure_trans/5.txt'], 'tests/closure_trans/5_res.txt')
        t2.test('Prikaz "closure_trans" #6 Mnozina', ['tests/closure_trans/6.txt'], intentional_error=True)
        t2.test('Prikaz "closure_trans" #7 Univerzum', ['tests/closure_trans/7.txt'], intentional_error=True)
        t2.test('Prikaz "closure_trans" #8 Zadny parametr', ['tests/closure_trans/no_param.txt'], intentional_error=True)
        t2.test('Prikaz "closure_trans" #9 Moc parametru', ['tests/closure_trans/too_many.txt'], intentional_error=True)

        # Command select
        t2.test('Prikaz "select" #1 Jednoprvkova mnozina', ['tests/select/1.txt'], 'tests/select/1_res.txt')
        t2.test('Prikaz "select" #2 Jednoprvkova relace', ['tests/select/2.txt'], 'tests/select/2_res.txt')
        t2.test('Prikaz "select" #3 Prazdna mnozina', ['tests/select/3.txt'], 'tests/select/3_res.txt')
        t2.test('Prikaz "select" #4 Nevykonany radek', ['tests/select/4.txt'], 'tests/select/4_res.txt')
        t2.test('Prikaz "select" #5 Skok na neexistujici radek', ['tests/select/5.txt'], intentional_error=True)
        t2.test('Prikaz "select" #6 Pristup na neexistujici radek', ['tests/select/6.txt'], intentional_error=True)
        t2.test('Prikaz "select" #7 Prazdna relace', ['tests/select/7.txt'], 'tests/select/7_res.txt')
        t2.test('Prikaz "select" #8 Zadny parametr', ['tests/select/no_param.txt'], intentional_error=True)
        t2.test('Prikaz "select" #9 Moc parametru', ['tests/select/too_many.txt'], intentional_error=True)


        # Self modifying tests
        # t2.test('Sebeupravujici radky #1 Jeden complement', ['tests/self_mod/1.txt'], 'tests/self_mod/1_res.txt')
        # t2.test('Sebeupravujici radky #2 Tri complementy', ['tests/self_mod/2.txt'], 'tests/self_mod/2_res.txt')
        # t2.test('Sebeupravujici radky #3 Tri iterace (union+complement)', ['tests/self_mod/3.txt'], 'tests/self_mod/3_res.txt')


    print('-- STATISTIKA --')
    print('Zakladni reseni:')
    t1.print_stats()

    if args.bonus:
        print('Bonusove reseni')
        t2.print_stats()

    if valgrind:
        os.remove(VALGRIND_LOG)
