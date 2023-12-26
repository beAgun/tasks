def convert_to_roman(n):
    roman_symbols = ['I', 'V', 'X', 'L', 'C', 'D', 'M']

    rest_digits = ''
    if n <= 1000:
        digits = list((map(int, str(n))))
    else:
        digits = list((map(int, str(n)[:2])))
        rest_digits = ''.join(str(n)[2:])

    ans = ''
    for i, digit in enumerate(reversed(digits)):
        i = 2*i
        if digit == 0 and i == 0:
            continue
        if digit < 5 - 1:
            ans = roman_symbols[i] * digit + ans
        elif digit == 4:
            ans = roman_symbols[i] + roman_symbols[i + 1] + ans
        elif 5 <= digit < 9:
            ans = roman_symbols[i + 1] + roman_symbols[i] * (digit - 5) + ans
        elif digit == 9:
            ans = roman_symbols[i] + roman_symbols[i + 2] + ans
    ans += rest_digits
    return ans


def main():
    try:
        n = int(input('Input any integer number from 1 to 10^5: '))
        assert n < 10**5
    except AssertionError:
        print('Incorrect input!')

    print(n, convert_to_roman(n))


if __name__ == '__main__':
    main()
