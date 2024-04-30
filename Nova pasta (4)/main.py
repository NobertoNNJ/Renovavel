from sol import execute as sol_execute
from vento import execute as vento_execute


res = int(input("Digite 1 para ver geração por vento, 2 para geração solar: "))

match res:
    case 1:
        vento_execute()
    case 2:
        sol_execute()
    case _:
        print("Opção inválida")