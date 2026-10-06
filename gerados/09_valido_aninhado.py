# Gerado pelo MemeScript 1.0.0
# Variáveis recebem o prefixo ms_var_ para preservar seus nomes.
ms_var_i = 0
ms_var_j = 0

while (ms_var_i < 2):
    ms_var_j = 0
    while (ms_var_j < 3):
        ms_var_j = (ms_var_j + 1)
        if (ms_var_j == 2):
            break
        print(ms_var_i, ms_var_j)
    ms_var_i = (ms_var_i + 1)
print('Fim:', ms_var_i, ms_var_j)
