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
from typing import Counter

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
    t1.test('Prikaz "empty" #5 Moc parametru', ['test/empty/too_many.txt'], intentional_error=True)

    # Command card
    t1.test('Prikaz "card" #1 Prazdna mnozina', ['tests/card/0.txt'], 'tests/card/0_res.txt')
    t1.test('Prikaz "card" #2 Mnozina o velikosti 1', ['tests/card/1.txt'], 'tests/card/1_res.txt')
    t1.test('Prikaz "card" #3 Mnozina o velikosti 5', ['tests/card/2.txt'], 'tests/card/2_res.txt')
    t1.test('Prikaz "card" #4 Relace', ['tests/card/3.txt'], intentional_error=True)
    t1.test('Prikaz "card" #5 Zadny parametr', ['tests/card/no_param.txt'], intentional_error=True)
    t1.test('Prikaz "card" #6 Moc parametru', ['tests/card/too_many.txt'], intentional_error=True)

    if args.bonus:
        # Bonusove reseni
        pass

    print('-- STATISTIKA --')
    print('Zakladni reseni:')
    t1.print_stats()

    if args.bonus:
        print('Bonusove reseni')
        t2.print_stats()
