
alphabet_1 = [
    "sol", "luna", "mar", "rio",
    "fuego", "aire", "tierra", "nube",
    "roca", "bosque", "nieve", "trueno",
    "flor", "sombra", "luz", "viento"
]

class AlphabetProvider:

    alphabet_dictionary = {'test_16bits_alph': alphabet_1}

    @classmethod
    def provide_alphabet(cls, key):
        return cls.alphabet_dictionary.get(key)