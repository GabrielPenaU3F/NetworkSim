# Test alphabet
from src.physical_layer.codebook import Codebook

def make_test_codebook():
    alphabet = [
            "sol", "luna", "mar", "rio",
            "fuego", "aire", "tierra", "nube",
            "roca", "bosque", "nieve", "trueno",
            "flor", "sombra", "luz", "viento"
        ]
    return Codebook(alphabet)

if __name__ == "__main__":
    codebook = make_test_codebook()
    codebook.analyze_code()
