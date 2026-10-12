#!/usr/bin/env python3
# The FinalOrder — consultas públicas e validação local
# Não coleta nem agrega dados pessoais privados. CPF é apenas validado localmente.

import json
import re
import urllib.error
import urllib.request

TITLE = "The FinalOrder"
UNDERLINE = "_" * 32
LANG = "pt"

TEXT = {
    "pt": {
        "cpf": "Digite o CPF (somente validação local): ",
        "cpf_ok": "CPF válido matematicamente. Isso NÃO confirma identidade nem consulta cadastro.",
        "cpf_bad": "CPF inválido.",
        "cep": "Digite o CEP: ",
        "cep_bad": "CEP inválido. Informe 8 dígitos.",
        "cep_fail": "Não foi possível consultar o CEP. Verifique a conexão e tente novamente.",
        "cnpj": "Digite o CNPJ: ",
        "cnpj_bad": "CNPJ inválido. Informe 14 dígitos.",
        "cnpj_fail": "Não foi possível consultar dados públicos do CNPJ.",
        "email": "Digite o e-mail para validar o formato: ",
        "email_ok": "Formato de e-mail aparentemente válido; isso não confirma que a conta existe.",
        "email_bad": "Formato de e-mail inválido.",
        "name": "Digite o nome para organizar uma pesquisa manual em fontes públicas: ",
        "name_note": "Este programa não busca nem revela CPF, endereço, parentes ou outros dados privados pelo nome.",
        "phone": "Digite o telefone para normalizar o formato: ",
        "phone_note": "Número normalizado (somente formatação); não consulta titular ou cadastro.",
        "options": "Opções",
        "language": "Idioma",
        "invalid": "Opção inválida.",
        "back": "Pressione Enter para voltar ao menu...",
        "exit": "Saindo.",
        "public": "Consulta de dados públicos da empresa",
    },
    "en": {
        "cpf": "Enter CPF (local validation only): ",
        "cpf_ok": "CPF passes mathematical validation. This does NOT verify identity or query records.",
        "cpf_bad": "Invalid CPF.",
        "cep": "Enter Brazilian postal code (CEP): ",
        "cep_bad": "Invalid CEP. Enter 8 digits.",
        "cep_fail": "Could not query CEP. Check your connection and try again.",
        "cnpj": "Enter CNPJ: ",
        "cnpj_bad": "Invalid CNPJ. Enter 14 digits.",
        "cnpj_fail": "Could not retrieve public CNPJ data.",
        "email": "Enter email to validate its format: ",
        "email_ok": "Email format looks valid; this does not confirm the account exists.",
        "email_bad": "Invalid email format.",
        "name": "Enter a name for manual research in public sources: ",
        "name_note": "This program does not retrieve CPF, addresses, relatives, or other private data by name.",
        "phone": "Enter phone number to normalize its format: ",
        "phone_note": "Normalized number (formatting only); no subscriber lookup.",
        "options": "Options",
        "language": "Language",
        "invalid": "Invalid option.",
        "back": "Press Enter to return to the menu...",
        "exit": "Exiting.",
        "public": "Public company information lookup",
    },
    "ru": {
        "cpf": "Введите CPF (только локальная проверка): ",
        "cpf_ok": "CPF прошёл математическую проверку. Личность и записи не проверяются.",
        "cpf_bad": "Неверный CPF.",
        "cep": "Введите бразильский почтовый индекс (CEP): ",
        "cep_bad": "Неверный CEP. Нужно 8 цифр.",
        "cep_fail": "Не удалось получить CEP. Проверьте подключение.",
        "cnpj": "Введите CNPJ: ",
        "cnpj_bad": "Неверный CNPJ. Нужно 14 цифр.",
        "cnpj_fail": "Не удалось получить открытые данные CNPJ.",
        "email": "Введите email для проверки формата: ",
        "email_ok": "Формат email выглядит верным; существование аккаунта не подтверждается.",
        "email_bad": "Неверный формат email.",
        "name": "Введите имя для ручного поиска в открытых источниках: ",
        "name_note": "Программа не ищет CPF, адреса, родственников или другие закрытые данные по имени.",
        "phone": "Введите телефон для нормализации формата: ",
        "phone_note": "Номер отформатирован; поиск владельца не выполняется.",
        "options": "Настройки",
        "language": "Язык",
        "invalid": "Неверный пункт.",
        "back": "Нажмите Enter, чтобы вернуться в меню...",
        "exit": "Выход.",
        "public": "Открытые данные компании",
    },
}

def digits(value):
    return re.sub(r"\D", "", value)

def valid_cpf(value):
    cpf = digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    total = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = (total * 10 % 11) % 10
    total = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = (total * 10 % 11) % 10
    return cpf[-2:] == f"{d1}{d2}"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheFinalOrder/1.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))

def lookup_cep():
    t = TEXT[LANG]
    cep = digits(input(t["cep"]))
    if len(cep) != 8:
        print(t["cep_bad"])
        return
    try:
        data = fetch_json(f"https://viacep.com.br/ws/{cep}/json/")
        if data.get("erro"):
            print(t["cep_fail"])
            return
        for key, label in [
            ("cep", "CEP"), ("logradouro", "Rua"), ("bairro", "Bairro"),
            ("localidade", "Cidade"), ("uf", "Estado")
        ]:
            print(f"{label}: {data.get(key, '')}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        print(t["cep_fail"])

def valid_cnpj(value):
    c = digits(value)
    if len(c) != 14 or c == c[0] * 14:
        return False
    def calc(part, weights):
        s = sum(int(n) * w for n, w in zip(part, weights))
        r = s % 11
        return "0" if r < 2 else str(11 - r)
    d1 = calc(c[:12], [5,4,3,2,9,8,7,6,5,4,3,2])
    d2 = calc(c[:12] + d1, [6,5,4,3,2,9,8,7,6,5,4,3,2])
    return c[-2:] == d1 + d2

def lookup_cnpj():
    t = TEXT[LANG]
    cnpj = digits(input(t["cnpj"]))
    if not valid_cnpj(cnpj):
        print(t["cnpj_bad"])
        return
    try:
        data = fetch_json(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
        # Only show ordinary public company-registration fields.
        fields = [
            ("razao_social", "Razão social"), ("nome_fantasia", "Nome fantasia"),
            ("descricao_situacao_cadastral", "Situação cadastral"),
            ("data_inicio_atividade", "Início da atividade"),
            ("municipio", "Município"), ("uf", "UF"),
            ("cnae_fiscal_descricao", "Atividade principal"),
        ]
        for key, label in fields:
            value = data.get(key)
            if value:
                print(f"{label}: {value}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        print(t["cnpj_fail"])

def pause():
    input("\n" + TEXT[LANG]["back"])

def menu():
    global LANG
    while True:
        t = TEXT[LANG]
        print("\n" + TITLE.center(32))
        print(UNDERLINE)
        print("[1] CPF")
        print("[2] CEP")
        print("[3] CNPJ")
        print("[4] Email")
        print("[5] Nome Completo")
        print("[6] Telefone")
        print("[7] Opções")
        choice = input("\n> ").strip()

        if choice == "1":
            value = input(t["cpf"])
            print(t["cpf_ok"] if valid_cpf(value) else t["cpf_bad"])
            pause()
        elif choice == "2":
            lookup_cep()
            pause()
        elif choice == "3":
            print(t["public"])
            lookup_cnpj()
            pause()
        elif choice == "4":
            value = input(t["email"]).strip()
            ok = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))
            print(t["email_ok"] if ok else t["email_bad"])
            pause()
        elif choice == "5":
            input(t["name"])
            print(t["name_note"])
            pause()
        elif choice == "6":
            value = input(t["phone"])
            normalized = digits(value)
            print(f"{t['phone_note']} {normalized}")
            pause()
        elif choice == "7":
            print(f"\n{t['options']}")
            print("[1] English")
            print("[2] Russian")
            print("[3] Portuguese")
            lang_choice = input("> ").strip()
            LANG = {"1": "en", "2": "ru", "3": "pt"}.get(lang_choice, LANG)
        elif choice in ("0", "q", "sair", "exit"):
            print(t["exit"])
            break
        else:
            print(t["invalid"])

if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado.")
