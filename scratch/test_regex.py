import re

def corregir_formato(texto):
    # 1. Decode RTF hex escapes like \'e1, \'c9
    def decode_hex(match):
        try:
            return bytes.fromhex(match.group(1)).decode('cp1252')
        except:
            return match.group(0)
    
    texto = re.sub(r"\\\'([0-9a-fA-F]{2})", decode_hex, texto)
    
    # 2. Remove RTF tags
    texto = re.sub(r'\{|\}|\\[a-z]+-?\d*\s?', '', texto)
    return texto.strip()

test_cases = [
    "1 Éstas {\\i\\cf15son} las generaciones",
    "\\par{\\qc\\b\\fs28 La maldad",
    "9 \\par{\\qc\\b\\fs28 El diluvio\\par} \\'c9sta es la historia",
    "resinosa,{\\cf2\\b\\super [o]} hazle",
    "respondió el criado. \\'bfDebo entonces",
    "6 \\'a1De ningu",
    "Luego dijeron: \\'abConstruyamos una ciudad"
]

for tc in test_cases:
    print(f"Original: {tc}")
    print(f"Corrected: {corregir_formato(tc)}")
    print("-" * 20)
