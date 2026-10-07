# Gerado pelo MemeScript 1.0.0
# Variáveis recebem o prefixo ms_var_ para preservar seus nomes.
ms_var_energia = 0
ms_var_cafes = 0
ms_var_limite = 0
ms_var_preco = float(4.5)
ms_var_gasto = float(0)
ms_var_pedido = 'QUERO CAFEEEEEEE!'

print('Qual o limite de cafés?')
ms_var_limite = int(input())
while (ms_var_cafes < ms_var_limite):
    ms_var_cafes = (ms_var_cafes + 1)
    ms_var_energia = ((ms_var_energia + 2) + (3 * 4))
    ms_var_gasto = float((ms_var_cafes * ms_var_preco))
    print('Cafés:', ms_var_cafes, 'Energia:', ms_var_energia)
    if (ms_var_energia >= 67):
        print('Já estou elétrico!')
        break
    else:
        print(ms_var_pedido)
print('Energia final:', ms_var_energia)
print('Gasto:', ms_var_gasto)
print('Precedência:', (2 + (3 * 4)))
print('Parênteses:', ((2 + 3) * 4))
