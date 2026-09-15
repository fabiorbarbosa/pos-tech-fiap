"""Anonimização simples de dados médicos (LGPD).

Remove/mascara identificadores diretos: nomes próprios, CPF, RG, telefone,
e-mail, datas de nascimento e números de prontuário. Baseada em regras +
gazetteer mínimo — suficiente para dados sintéticos do projeto; para produção,
usar modelo NER + validação humana.
"""
import re

_PATTERNS = [
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    (re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]\b"), "[RG]"),
    (re.compile(r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b"), "[TELEFONE]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    (re.compile(r"\b\d{2}/\d{2}/\d{4}\b"), "[DATA]"),
    (re.compile(r"\b(prontu[áa]rio|registro)\s*n?[º°:]?\s*\d+\b", re.I), "[PRONTUARIO]"),
    (re.compile(r"\b(Dra?\.?|Dr[a]?\.?)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚáéíóúâêôãõç]+(\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wáéíóúâêôãõç]+)+"), r"\1 [NOME]"),
    (re.compile(r"\b(atendeu( a)?|paciente|respons[aá]vel|m[eé]dico[a]?)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wáéíóúâêôãõçç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wáéíóúâêôãõçç]+)+)"),
     r"\1 [NOME]"),
]


def anonymize(text: str) -> str:
    for rx, repl in _PATTERNS:
        text = rx.sub(repl, text)
    return re.sub(r"\s{2,}", " ", text).strip()


if __name__ == "__main__":  # verificação rápida
    raw = "Dr. João Silva (CPF 123.456.789-00, tel (11) 98765-4321) atendeu Maria Souza, nascida em 12/03/1980, prontuário nº 456789. Contato: joao@hospital.br"
    out = anonymize(raw)
    print(out)
    assert "123.456.789-00" not in out and "João Silva" not in out and "12/03/1980" not in out
    print("OK")
